from config import (
    DATA_FOLDER,
    SUPPORTED_FILES,
)

from ingest import index_file


def index_all_documents():
    """
    Scan data folder and index only new/modified files.
    """

    print("\nScanning data folder...\n")

    total_files = 0

    for file in DATA_FOLDER.iterdir():

        if not file.is_file():
            continue

        if file.suffix.lower() not in SUPPORTED_FILES:
            continue

        total_files += 1

        index_file(file)

    print("\n======================================")
    print(f"Total Supported Files : {total_files}")
    print("Database is up to date.")
    print("======================================\n")