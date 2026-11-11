"""
Core text analysis logic.
"""

import math
import re
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

# Silent reading speed used when the caller does not pass one.
DEFAULT_WPM = 200

# Periods between digits belong to numbers (3.14, 1.2.3, 10.0.0.1), not sentences.
_DECIMAL_PERIOD = re.compile(r"(?<=\d)\.(?=\d)")
# ASCII terminators, plus the ideographic period and fullwidth ! ? used in CJK text.
_SENTENCE_END = re.compile(r"[.!?。！？]+")
# A blank line, including one that contains only spaces or tabs. Newlines are normalized first.
_PARAGRAPH_BREAK = re.compile(r"\n[^\S\n]*\n")
# Strip punctuation that is stuck to the outside of a word. Keep apostrophes and interior hyphens.
_EDGE_PUNCTUATION = re.compile(r"^[^\w'’]+|[^\w'’]+$")


def _validate_wpm(wpm):
    if (
        isinstance(wpm, bool)
        or not isinstance(wpm, (int, float))
        or not math.isfinite(wpm)
        or wpm <= 0
    ):
        raise ValueError("wpm must be a positive number")


def _reading_minutes(words, wpm):
    """Minutes, rounded half-up to two decimals so 0.045 does not become 0.04."""
    if not words:
        return 0.0
    minutes = Decimal(words) / Decimal(str(wpm))
    return float(minutes.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _sentence_count(text):
    without_decimal_periods = _DECIMAL_PERIOD.sub("", text)
    return len(_SENTENCE_END.findall(without_decimal_periods))


def _paragraph_count(text):
    # Convert CRLF and classic Mac CR breaks without turning a single CRLF into a blank line.
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    parts = _PARAGRAPH_BREAK.split(normalized)
    return sum(1 for part in parts if part.strip())


def _average_word_length(tokens):
    lengths = []
    for token in tokens:
        core = _EDGE_PUNCTUATION.sub("", token)
        if core:
            lengths.append(len(core))
    if not lengths:
        return 0
    return sum(lengths) / len(lengths)


def analyze_text(text, wpm=DEFAULT_WPM):
    """Analyze text and return statistics.

    ``wpm`` is the reading speed used for ``reading_time_minutes``. It must be
    a positive, finite number. Callers that omit it get 200 words per minute.

    Word length ignores punctuation attached to either end of a token, so
    ``world.`` counts as five characters. Punctuation-only tokens still count
    as words, matching a whitespace split, but they do not affect the average.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    _validate_wpm(wpm)

    # A leading BOM is an encoding artifact, not text content.
    if text.startswith("\ufeff"):
        text = text[1:]

    chars = len(text)
    chars_no_spaces = len("".join(text.split()))
    tokens = text.split()
    words = len(tokens)
    lines = len(text.splitlines())
    sentences = _sentence_count(text)
    paragraphs = _paragraph_count(text)
    avg_word_length = _average_word_length(tokens)

    # Simplified Flesch Reading Ease: syllables are approximated as word length / 5.
    if sentences > 0 and words > 0:
        avg_sentence_length = words / sentences
        readability = round(
            206.835 - 1.015 * avg_sentence_length - 84.6 * (avg_word_length / 5),
            1,
        )
    else:
        readability = 0

    reading_time_minutes = _reading_minutes(words, wpm)

    return {
        "characters": chars,
        "characters_no_spaces": chars_no_spaces,
        "words": words,
        "lines": lines,
        "sentences": sentences,
        "paragraphs": paragraphs,
        "avg_word_length": round(avg_word_length, 2),
        "readability_score": readability,
        "reading_time_minutes": reading_time_minutes,
    }


def analyze_file(file_path, wpm=DEFAULT_WPM):
    """Analyze a UTF-8 text file.

    A leading byte-order mark is ignored. ``wpm`` is forwarded to
    :func:`analyze_text`. Missing files, directories, and decoding errors are
    raised to the caller.
    """
    content = Path(file_path).read_text(encoding="utf-8-sig")
    return analyze_text(content, wpm=wpm)
