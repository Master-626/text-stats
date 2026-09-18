# Text Stats

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)

Analyze text files: word count, character count, readability, and more.

## 🌟 Features

- 📊 **Detailed Stats** - Characters, words, lines, sentences, paragraphs
- 📖 **Readability** - Estimate readability score
- 📄 **File Analysis** - Analyze entire text files
- 🎨 **Rich Output** - Beautiful colored terminal tables
- 🐍 **Python API** - Use as a library in your code

## 📦 Installation

```bash
git clone https://github.com/Master-626/text-stats.git
cd text-stats
pip install .
```

## 🚀 Usage

### Analyze a File
```bash
text-stats analyze -f README.md
```

### Analyze Text String
```bash
text-stats analyze -t "Hello world! This is a test."
```

## 🐍 Python API

```python
from text_stats import analyze_text, analyze_file

# Analyze text
stats = analyze_text("Hello world! This is a test.")
print(f"Words: {stats['words']}")
print(f"Readability: {stats['readability_score']}")

# Analyze file
stats = analyze_file("document.txt")
```

## 🧪 Testing

```bash
pip install -e ".[dev]"
pytest
```

## 📄 License

MIT License
