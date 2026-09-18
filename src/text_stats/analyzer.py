"""
Core text analysis logic.
"""

import re
from pathlib import Path
from typing import Dict


def analyze_text(text: str) -> Dict:
    """Analyze text and return statistics."""
    # Basic counts
    chars = len(text)
    chars_no_spaces = len(text.replace(" ", "").replace("\n", ""))
    words = len(text.split())
    lines = len(text.splitlines())

    # Sentences (rough estimate)
    sentences = len(re.findall(r'[.!?]+', text))

    # Paragraphs
    paragraphs = len([p for p in text.split("\n\n") if p.strip()])

    # Average word length
    if words > 0:
        avg_word_length = sum(len(w) for w in text.split()) / words
    else:
        avg_word_length = 0

    # Readability estimate (Flesch Reading Ease approximation)
    if sentences > 0 and words > 0:
        avg_sentence_length = words / sentences
        # Simplified readability score
        readability = round(206.835 - 1.015 * avg_sentence_length - 84.6 * (avg_word_length / 5), 1)
    else:
        readability = 0

    return {
        "characters": chars,
        "characters_no_spaces": chars_no_spaces,
        "words": words,
        "lines": lines,
        "sentences": sentences,
        "paragraphs": paragraphs,
        "avg_word_length": round(avg_word_length, 2),
        "readability_score": readability,
    }


def analyze_file(file_path: str) -> Dict:
    """Analyze a text file."""
    content = Path(file_path).read_text(encoding="utf-8")
    return analyze_text(content)
