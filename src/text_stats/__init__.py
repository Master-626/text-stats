"""
text-stats - Analyze text files with detailed statistics.

Counts characters, words, lines, sentences, and paragraphs, estimates a
readability score, and reports how long the text takes to read.
"""

from .analyzer import analyze_file, analyze_text

__version__ = "0.1.0"
__all__ = ["analyze_text", "analyze_file"]
