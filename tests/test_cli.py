import subprocess
import sys

import pytest
from click.testing import CliRunner

from text_stats import __version__
from text_stats.cli import main

runner = CliRunner()


def test_help_lists_analyze_and_reading_speed():
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "analyze" in result.output

    result = runner.invoke(main, ["analyze", "--help"])
    assert result.exit_code == 0
    assert "--file" in result.output
    assert "--text" in result.output
    assert "--wpm" in result.output


def test_version_uses_the_program_name():
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == f"text-stats, version {__version__}"


def test_analyze_text_prints_stats():
    result = runner.invoke(main, ["analyze", "-t", "Hello world."])
    assert result.exit_code == 0
    assert "Words" in result.output
    assert "Sentences" in result.output
    assert "Readability Score" in result.output
    assert "Reading Time (min)" in result.output
    assert "0.01" in result.output
    assert result.exception is None


def test_missing_input_is_an_error():
    result = runner.invoke(main, ["analyze"])
    assert result.exit_code == 2
    assert "--file" in result.output or "file" in result.output.lower()


def test_empty_text_is_analyzed():
    result = runner.invoke(main, ["analyze", "-t", ""])
    assert result.exit_code == 0
    assert "Words" in result.output
    assert "0.00" in result.output


def test_file_and_text_together_are_rejected(tmp_path):
    path = tmp_path / "note.txt"
    path.write_text("Hello.", encoding="utf-8")
    result = runner.invoke(main, ["analyze", "-f", str(path), "-t", "Other"])
    assert result.exit_code == 2
    assert "only one" in result.output.lower()


def test_analyze_file_and_custom_reading_speed(tmp_path):
    path = tmp_path / "words.txt"
    path.write_text(" ".join(["word"] * 100), encoding="utf-8")
    result = runner.invoke(main, ["analyze", "-f", str(path), "--wpm", "50"])
    assert result.exit_code == 0
    assert str(path) in result.output
    assert "2.00" in result.output


def test_invalid_reading_speed_is_rejected():
    result = runner.invoke(main, ["analyze", "-t", "Hello", "--wpm", "0"])
    assert result.exit_code != 0


def test_missing_file_is_a_clean_error(tmp_path):
    result = runner.invoke(main, ["analyze", "-f", str(tmp_path / "missing.txt")])
    assert result.exit_code == 1
    assert "No such file" in result.output
    assert "Traceback" not in result.output


def test_directory_is_a_clean_error(tmp_path):
    result = runner.invoke(main, ["analyze", "-f", str(tmp_path)])
    assert result.exit_code == 1
    assert "directory" in result.output.lower()
    assert "Traceback" not in result.output


def test_non_utf8_file_is_a_clean_error(tmp_path):
    path = tmp_path / "bad.txt"
    path.write_bytes(b"\xff\xfe\x00hello")
    result = runner.invoke(main, ["analyze", "-f", str(path)])
    assert result.exit_code == 1
    assert "UTF-8" in result.output
    assert "Traceback" not in result.output


def test_bracket_filenames_are_printed_literally(tmp_path):
    path = tmp_path / "[red]note.txt"
    path.write_text("Hi.", encoding="utf-8")
    result = runner.invoke(main, ["analyze", "-f", str(path)])
    assert result.exit_code == 0
    assert "[red]note.txt" in result.output

    folder = tmp_path / "x["
    folder.mkdir()
    tricky = folder / "].txt"
    tricky.write_text("Hi.", encoding="utf-8")
    result = runner.invoke(main, ["analyze", "-f", str(tricky)])
    assert result.exit_code == 0
    assert "x[/].txt" in result.output
    assert result.exception is None


def test_module_entrypoint_prints_version():
    result = subprocess.run(
        [sys.executable, "-m", "text_stats", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert __version__ in result.stdout


def test_installed_version_matches_package_metadata():
    import importlib.metadata as metadata

    try:
        installed = metadata.version("text-stats")
    except metadata.PackageNotFoundError:
        pytest.skip("text-stats is not installed")
    assert installed == __version__
