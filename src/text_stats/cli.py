"""
CLI interface for text-stats.
"""

import click
from rich.console import Console
from rich.table import Table

from . import __version__
from .analyzer import DEFAULT_WPM, analyze_file, analyze_text

# markup is off so file paths that contain brackets are printed literally.
console = Console(markup=False)


@click.group()
@click.version_option(__version__, prog_name="text-stats")
def main():
    """Text Stats - Analyze text files with detailed statistics."""


@main.command()
@click.option("-f", "--file", "file_path", help="UTF-8 text file to analyze.")
@click.option("-t", "--text", help="Text string to analyze.")
@click.option(
    "--wpm",
    default=DEFAULT_WPM,
    show_default=True,
    type=click.IntRange(min=1),
    help="Reading speed in words per minute, used for the reading-time estimate.",
)
def analyze(file_path, text, wpm):
    """Analyze text and show statistics."""
    if file_path is not None and text is not None:
        raise click.UsageError("Provide only one of --file or --text, not both.")

    if file_path is not None:
        try:
            stats = analyze_file(file_path, wpm=wpm)
        except FileNotFoundError as exc:
            raise click.FileError(file_path, hint="No such file or directory.") from exc
        except IsADirectoryError as exc:
            raise click.FileError(file_path, hint="Path is a directory, not a file.") from exc
        except UnicodeDecodeError as exc:
            raise click.FileError(file_path, hint="File is not valid UTF-8 text.") from exc
        except OSError as exc:
            raise click.FileError(file_path, hint=str(exc)) from exc
        console.print(f"\n📄 File: {file_path}")
    elif text is not None:
        stats = analyze_text(text, wpm=wpm)
        console.print("\n📝 Text Analysis")
    else:
        raise click.UsageError("Please provide either --file or --text.")

    table = Table(show_header=False, box=None)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Characters", str(stats["characters"]))
    table.add_row("Characters (no spaces)", str(stats["characters_no_spaces"]))
    table.add_row("Words", str(stats["words"]))
    table.add_row("Lines", str(stats["lines"]))
    table.add_row("Sentences", str(stats["sentences"]))
    table.add_row("Paragraphs", str(stats["paragraphs"]))
    table.add_row("Avg Word Length", str(stats["avg_word_length"]))
    table.add_row("Readability Score", str(stats["readability_score"]))
    table.add_row("Reading Time (min)", f"{stats['reading_time_minutes']:.2f}")

    console.print(table)


if __name__ == "__main__":
    main()
