from pathlib import Path
import pytest
from investigator.tools.filesystem import inspect_file


def test_inspect_file_reads_text_file(tmp_path: Path) -> None:
    file_path = tmp_path / "example.py"
    file_path.write_text(
        "print('hello')\n"
        "print('world')\n",
        encoding="utf-8",
    )

    result = inspect_file(str(file_path))

    assert result["path"] == str(file_path)
    assert result["content"] == (
        "print('hello')\n"
        "print('world')\n"
    )
    assert result["line_count"] == 2


def test_inspect_file_raises_for_missing_file(tmp_path: Path) -> None:
    file_path = tmp_path / "missing.py"

    with pytest.raises(FileNotFoundError):
        inspect_file(str(file_path))


def test_inspect_file_raises_for_directory(tmp_path: Path) -> None:
    with pytest.raises(IsADirectoryError):
        inspect_file(str(tmp_path))


def test_inspect_file_rejects_invalid_utf8(tmp_path: Path) -> None:
    file_path = tmp_path / "binary.dat"
    file_path.write_bytes(b"\xff\xfe\xfd")

    with pytest.raises(ValueError):
        inspect_file(str(file_path))