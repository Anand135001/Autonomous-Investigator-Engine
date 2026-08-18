from pathlib import Path
from typing import Any

def inspect_file(path: str) -> dict[str, Any]:
    """
    Read a UTF-* file and return structured inspection data.
    
    currently function is not design to modify the file
    """

    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File does not exists: {file_path}")

    if not file_path.is_file():
        raise IsADirectoryError(f"Path is not a file: {file_path}")

    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"file is not UTF-8 text: {file_path}"
        ) from exc

    return {
        "path": str(file_path),
        "content": content,
        "line_count": len(content.splitlines())
    }