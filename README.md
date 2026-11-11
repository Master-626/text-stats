# Text Stats

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)

## 中文简介

text-stats 是一个轻量的纯文本统计工具，可当作命令行或 Python 库使用。它统计字符、不含空白的字符、词、行、句子、段落和平均词长，给出一个粗略的可读性分数，并按阅读速度估算阅读时间。

```bash
pip install .
text-stats analyze -f README.md
text-stats analyze -t "你好。这是一个例子。"
```

开发依赖与检查：`pip install -e ".[dev]"`，然后运行 `ruff check .` 和 `pytest`。词数按空白切分，不会做中文分词；句子统计会识别 `。！？`。

## Purpose

text-stats measures a string or a UTF-8 text file. Use it from the terminal when you want a quick count, or import it when another program needs the same numbers.

The command is installed as both `text-stats` and `tstat`. `python -m text_stats` runs the same program.

## Installation

From a checkout of this repository:

```bash
pip install .
```

To work on the code, install the test and lint tools as well:

```bash
pip install -e ".[dev]"
```

Requires Python 3.8 or newer. Runtime dependencies are [Click](https://click.palletsprojects.com/) and [Rich](https://rich.readthedocs.io/).

## Usage

Analyze a file:

```bash
text-stats analyze -f notes.txt
```

Analyze a string:

```bash
text-stats analyze -t "Hello world. The price is 3.14 today."
```

```text
📝 Text Analysis
 Characters              37
 Characters (no spaces)  31
 Words                   7
 Lines                   1
 Sentences               2
 Paragraphs              1
 Avg Word Length         4.14
 Readability Score       133.2
 Reading Time (min)      0.04
```

Estimate reading time at another speed (words per minute):

```bash
text-stats analyze -f notes.txt --wpm 250
```

Pass only one of `--file` and `--text`. A missing file, a directory, or a file that is not UTF-8 text exits with status 1 and a short message. Omitting both options, or passing both, exits with status 2.

## Options

`text-stats analyze` accepts:

| Option | Description |
| --- | --- |
| `-f`, `--file PATH` | UTF-8 text file to analyze. A leading byte-order mark is ignored. |
| `-t`, `--text TEXT` | Text to analyze, including an empty string. |
| `--wpm INTEGER` | Reading speed used for the time estimate. Default: 200. Minimum: 1. |
| `--help` | Show help for the command. |
| `--version` | Show the program version. Pass this on `text-stats` itself, not on `analyze`. |

`tstat analyze` takes the same options.

## Python API

```python
from text_stats import analyze_text, analyze_file

stats = analyze_text("Hello world. The price is 3.14 today.")
print(stats["words"])                 # 7
print(stats["sentences"])             # 2
print(stats["readability_score"])     # 133.2
print(stats["reading_time_minutes"])  # 0.04

print(analyze_text("one two three", wpm=180)["reading_time_minutes"])  # 0.02

print(analyze_file("notes.txt")["paragraphs"])
```

`analyze_text` raises `TypeError` when `text` is not a string, and `ValueError` when `wpm` is not a positive finite number. `analyze_file` raises `FileNotFoundError`, `IsADirectoryError`, or `UnicodeDecodeError` for bad paths and leaves handling those to the caller.

`reading_time_minutes` is `words / wpm`, rounded half-up to two decimal places. It is `0.0` when there are no words.

## What each number means

| Field | Definition |
| --- | --- |
| `characters` | Every code point, including spaces and newlines. |
| `characters_no_spaces` | Characters left after all whitespace is removed (spaces, tabs, carriage returns, and other Unicode spaces). |
| `words` | Whitespace-separated tokens, the same idea as `wc -w`. A token that is only punctuation still counts. |
| `lines` | Result of `str.splitlines()`. A final newline does not add another line. |
| `sentences` | Runs of `.` `!` `?` `。` `！` `？`. Periods between digits (`3.14`, `1.2.3`, `10.0.0.1`) are not sentence breaks. A real period after a number still is: `See 3. Then go.` is two sentences. |
| `paragraphs` | Non-empty blocks separated by a blank line. The blank line may contain spaces or tabs. Breaks written as `\n`, `\r\n`, or `\r` are all recognized. One line break is not a new paragraph. |
| `avg_word_length` | Average length of tokens after punctuation stuck to either end is removed. Apostrophes and interior hyphens stay, so `it's` is 4 and `well-known` is 10. Punctuation-only tokens are left out of the average. |
| `readability_score` | Simplified Flesch Reading Ease. `0` means it was not computed because the text has no words or no sentence terminator. |
| `reading_time_minutes` | Estimated minutes at the chosen words-per-minute rate. |

The readability formula is:

```text
206.835 - 1.015 * (words / sentences) - 84.6 * (avg_word_length / 5)
```

`avg_word_length / 5` stands in for syllables per word. Higher means easier. This is only a rough English-oriented hint, and the value can fall outside 0–100. It is rounded to one decimal place.

## Tests and lint

```bash
pip install -e ".[dev]"
ruff check .
pytest
```

GitHub Actions runs both commands on Python 3.8, 3.9, 3.10, 3.11, 3.12, and 3.13.

## Known limitations

- Periods in abbreviations such as `Dr.`, `e.g.`, and `U.S.` are counted as sentence breaks.
- Chinese and Japanese text is not split into dictionary words. Characters with no space between them are one token, including across `。！？`. Sentence marks are still counted, but the word count and the reading time follow the whitespace split.
- Files must be UTF-8. Other encodings are reported as an error.

## License

MIT License. See [LICENSE](LICENSE).
