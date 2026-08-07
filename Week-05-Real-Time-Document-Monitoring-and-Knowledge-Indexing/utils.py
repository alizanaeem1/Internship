import json
import hashlib
from pathlib import Path

from config import LOG_FOLDER


# JSON file that stores indexed files
INDEX_FILE = LOG_FOLDER / "indexed_files.json"


def file_hash(file: Path) -> str:
    """
    Generate SHA256 hash of a file.
    """

    sha = hashlib.sha256()

    with open(file, "rb") as f:
        while True:
            chunk = f.read(8192)

            if not chunk:
                break

            sha.update(chunk)

    return sha.hexdigest()


def load_index() -> dict:
    """
    Load indexed_files.json safely.
    """

    if not INDEX_FILE.exists():
        return {}

    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except json.JSONDecodeError:
        print("Warning: indexed_files.json is corrupted. Creating new index.")
        return {}


def save_index(index: dict):
    """
    Save indexed_files.json
    """

    LOG_FOLDER.mkdir(exist_ok=True)

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=4)


def is_indexed(file: Path) -> bool:
    """
    Check if the file is already indexed.
    """

    index = load_index()

    current_hash = file_hash(file)

    return index.get(str(file)) == current_hash


def update_index(file: Path):
    """
    Update indexed_files.json after indexing.
    """

    index = load_index()

    index[str(file)] = file_hash(file)

    save_index(index)


def remove_from_index(file: Path):
    """
    Remove deleted file from index.
    """

    index = load_index()

    if str(file) in index:
        del index[str(file)]

    save_index(index)