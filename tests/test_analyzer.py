import pytest
from text_stats.analyzer import analyze_text


def test_analyze_basic_text():
    """Test basic text analysis."""
    text = "Hello world. This is a test. How are you?"
    stats = analyze_text(text)
    assert stats["words"] > 0
    assert stats["characters"] > 0
    assert stats["sentences"] == 3


def test_analyze_empty_text():
    """Test empty text."""
    stats = analyze_text("")
    assert stats["words"] == 0
    assert stats["characters"] == 0


def test_analyze_paragraphs():
    """Test paragraph counting."""
    text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
    stats = analyze_text(text)
    assert stats["paragraphs"] == 3
