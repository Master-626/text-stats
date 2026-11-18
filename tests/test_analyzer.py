import math

import pytest

from text_stats.analyzer import analyze_file, analyze_text


def test_analyze_basic_text():
    """Test basic text analysis."""
    text = "Hello world. This is a test. How are you?"
    stats = analyze_text(text)
    assert stats["words"] == 9
    assert stats["characters"] == len(text)
    assert stats["characters_no_spaces"] == len("".join(text.split()))
    assert stats["lines"] == 1
    assert stats["sentences"] == 3
    assert stats["paragraphs"] == 1
    assert stats["avg_word_length"] == 3.33
    assert stats["reading_time_minutes"] == 0.05  # 9 / 200 = 0.045, half-up


def test_analyze_empty_text():
    """Test empty text."""
    stats = analyze_text("")
    assert stats["words"] == 0
    assert stats["characters"] == 0
    assert stats["characters_no_spaces"] == 0
    assert stats["lines"] == 0
    assert stats["sentences"] == 0
    assert stats["paragraphs"] == 0
    assert stats["avg_word_length"] == 0
    assert stats["readability_score"] == 0
    assert stats["reading_time_minutes"] == 0.0


def test_analyze_paragraphs():
    """Test paragraph counting."""
    text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
    stats = analyze_text(text)
    assert stats["paragraphs"] == 3
    assert stats["sentences"] == 3


def test_whitespace_is_excluded_from_characters_no_spaces():
    """Tabs, carriage returns, and other whitespace are not 'characters'."""
    assert analyze_text("a b\nc")["characters_no_spaces"] == 3
    assert analyze_text("a\tb\tc")["characters_no_spaces"] == 3
    assert analyze_text("a\tb\tc")["words"] == 3
    assert analyze_text("hello\r\nworld\r\n")["characters"] == 14
    assert analyze_text("hello\r\nworld\r\n")["characters_no_spaces"] == 10
    assert analyze_text("hello\r\nworld\r\n")["lines"] == 2
    assert analyze_text("   \n\t  ")["characters_no_spaces"] == 0
    assert analyze_text("   \n\t  ")["words"] == 0
    assert analyze_text("a\u00a0b")["characters_no_spaces"] == 2


def test_decimal_points_are_not_sentences():
    """Periods inside numbers used to inflate the sentence count."""
    assert analyze_text("The price is 3.14 today.")["sentences"] == 1
    assert analyze_text("Use version 1.2.3 now.")["sentences"] == 1
    assert analyze_text("Connect to 10.0.0.1 now.")["sentences"] == 1
    assert analyze_text("The value is 3.14.")["sentences"] == 1
    # A period after a number is still a sentence boundary.
    assert analyze_text("See 3. Then go.")["sentences"] == 2


def test_repeated_punctuation_is_one_sentence():
    assert analyze_text("Wow!!!")["sentences"] == 1
    assert analyze_text("Wait...")["sentences"] == 1
    assert analyze_text("What?! Yes.")["sentences"] == 2


def test_cjk_sentence_punctuation():
    assert analyze_text("你好。世界！")["sentences"] == 2
    assert analyze_text("什么？！")["sentences"] == 1
    assert analyze_text("Hello。World.")["sentences"] == 2


def test_abbreviations_still_count_as_sentence_breaks():
    """Known limitation: a period in an abbreviation is a sentence break."""
    assert analyze_text("Dr. Smith went home.")["sentences"] == 2


def test_blank_lines_separate_paragraphs():
    assert analyze_text("First\n\nSecond")["paragraphs"] == 2
    assert analyze_text("First\n \nSecond")["paragraphs"] == 2
    assert analyze_text("First\n\t\nSecond")["paragraphs"] == 2
    assert analyze_text("First\n\n\n\nSecond")["paragraphs"] == 2
    assert analyze_text("First\r\n\r\nSecond")["paragraphs"] == 2
    assert analyze_text("First\r\rSecond")["paragraphs"] == 2
    # One line break is not a new paragraph, including Windows newlines.
    assert analyze_text("First\nSecond")["paragraphs"] == 1
    assert analyze_text("First\r\nSecond")["paragraphs"] == 1
    assert analyze_text("First\r\nSecond")["lines"] == 2


def test_average_word_length_ignores_surrounding_punctuation():
    assert analyze_text("Hello, world!")["avg_word_length"] == 5
    assert analyze_text("Hello world.")["avg_word_length"] == 5
    assert analyze_text("it's well-known.")["avg_word_length"] == 7
    # Punctuation-only tokens count as words but not toward the average.
    stats = analyze_text("Hello ... world")
    assert stats["words"] == 3
    assert stats["avg_word_length"] == 5
    assert analyze_text("...")["words"] == 1
    assert analyze_text("...")["avg_word_length"] == 0


def test_readability_uses_word_length_without_punctuation():
    """``Hello world.`` is two 5-letter words, so the period must not lower the score."""
    stats = analyze_text("Hello world.")
    assert stats["readability_score"] == 120.2
    assert analyze_text("Hello world")["readability_score"] == 0


def test_reading_time_uses_wpm():
    text = " ".join(["word"] * 400)
    assert analyze_text(text)["reading_time_minutes"] == 2.0
    assert analyze_text(text)["words"] == 400
    assert analyze_text(text, wpm=100)["reading_time_minutes"] == 4.0
    assert analyze_text("one", wpm=200)["reading_time_minutes"] == 0.01
    assert analyze_text("", wpm=100)["reading_time_minutes"] == 0.0


@pytest.mark.parametrize("wpm", [0, -5, True, False, "fast", math.nan, math.inf])
def test_reading_speed_must_be_a_positive_number(wpm):
    with pytest.raises(ValueError):
        analyze_text("Hello", wpm=wpm)


def test_non_string_text_is_rejected():
    with pytest.raises(TypeError):
        analyze_text(None)
    with pytest.raises(TypeError):
        analyze_text(b"Hello")


def test_leading_bom_is_not_content():
    stats = analyze_text("\ufeffHello world.")
    assert stats["characters"] == len("Hello world.")
    assert stats["words"] == 2
    assert stats["avg_word_length"] == 5


def test_result_contains_the_public_fields():
    stats = analyze_text("Hello.")
    assert set(stats) == {
        "characters",
        "characters_no_spaces",
        "words",
        "lines",
        "sentences",
        "paragraphs",
        "avg_word_length",
        "readability_score",
        "reading_time_minutes",
    }


def test_analyze_file_round_trip(tmp_path):
    path = tmp_path / "note.txt"
    path.write_text("Hello world.\n\nSecond line.", encoding="utf-8")
    assert analyze_file(path) == analyze_text("Hello world.\n\nSecond line.")


def test_analyze_file_ignores_utf8_bom(tmp_path):
    path = tmp_path / "bom.txt"
    path.write_bytes("Hello world.".encode("utf-8-sig"))
    stats = analyze_file(path)
    assert stats["characters"] == len("Hello world.")
    assert stats["words"] == 2
    assert stats["sentences"] == 1


def test_analyze_file_missing_directory_and_binary(tmp_path):
    with pytest.raises(FileNotFoundError):
        analyze_file(tmp_path / "missing.txt")
    with pytest.raises(IsADirectoryError):
        analyze_file(tmp_path)
    binary = tmp_path / "data.bin"
    binary.write_bytes(b"\xff\xfe hello")
    with pytest.raises(UnicodeDecodeError):
        analyze_file(binary)
