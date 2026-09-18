"""
CLI interface for text-stats.
"""

import click
from rich.console import Console
from rich.table import Table

from .analyzer import analyze_text, analyze_file

console = Console()


@click.group()
@click.version_option()
def main():
    """Text Stats - Analyze text files with detailed statistics."""
    pass


@main.command()
@click.option("-f", "--file", help="Text file to analyze")
@click.option("-t", "--text", help="Text string to analyze")
def analyze(file, text):
    """Analyze text and show statistics."""
    if file:
        stats = analyze_file(file)
        console.print(f"\n📄 File: {file}")
    elif text:
        stats = analyze_text(text)
        console.print(f"\n📝 Text Analysis")
    else:
        click.echo("❌ Please provide either --file or --text", err=True)
        return

    # Show results in a table
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

    console.print(table)


if __name__ == "__main__":
    main()
