from pathlib import Path
import time
import threading

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from config import DATA_FOLDER, SUPPORTED_FILES
from ingest import index_file, delete_file_vectors


DEBOUNCE_SECONDS = 3
timers = {}


def show_prompt():
    print("\n>>> ", end="", flush=True)


def is_temp_file(path: str) -> bool:
    """
    Ignore temporary files created by Word, OneDrive, Windows, or editors.
    """

    name = Path(path).name.lower()

    return (
        name.startswith("~$")
        or name.startswith("~wrd")
        or name.startswith("~wrl")
        or name.endswith(".tmp")
        or name.endswith(".crdownload")
        or name.endswith(".part")
    )


def is_supported_file(path: str) -> bool:
    file = Path(path)
    return file.suffix.lower() in SUPPORTED_FILES


def safe_index(file_path: str):
    """
    Safely index a file after it finishes saving.
    """

    if is_temp_file(file_path):
        return

    if not is_supported_file(file_path):
        return

    file = Path(file_path)

    if not file.exists():
        return

    print(f"\n📄 Processing: {file.name}")
    print("⏳ Waiting for file to finish saving...")

    time.sleep(1)

    for attempt in range(5):
        try:
            print(f"📥 Indexing: {file.name}")
            index_file(file, force=False)
            print(f"✅ Indexed: {file.name}")
            break

        except PermissionError:
            print(f"⚠ File locked, retrying... {attempt + 1}/5")
            time.sleep(2)

        except FileNotFoundError:
            return

        except Exception as e:
            print(f"❌ Watcher error while indexing {file.name}: {e}")
            break

    show_prompt()


def debounce_index(file_path: str):
    """
    Prevent repeated indexing when a file is modified multiple times quickly.
    """

    if is_temp_file(file_path):
        return

    if not is_supported_file(file_path):
        return

    if file_path in timers:
        timers[file_path].cancel()

    timer = threading.Timer(
        DEBOUNCE_SECONDS,
        safe_index,
        args=(file_path,),
    )

    timers[file_path] = timer
    timer.start()


class DocumentWatcher(FileSystemEventHandler):

    def on_created(self, event):
        if event.is_directory:
            return

        debounce_index(event.src_path)

    def on_modified(self, event):
        if event.is_directory:
            return

        debounce_index(event.src_path)

    def on_deleted(self, event):
        if event.is_directory:
            return

        file_path = event.src_path

        if is_temp_file(file_path):
            return

        if not is_supported_file(file_path):
            return

        if file_path in timers:
            timers[file_path].cancel()
            del timers[file_path]

        file = Path(file_path)

        print(f"\n🗑️ File deleted: {file.name}")

        delete_file_vectors(file)

        print("🧹 Removed document vectors")
        print("✅ Database updated")

        show_prompt()


def start_watcher():
    """
    Start real-time watcher for data folder and all subfolders.
    """

    observer = Observer()

    observer.schedule(
        DocumentWatcher(),
        str(DATA_FOLDER),
        recursive=True,
    )

    observer.start()

    print("✅ Real-Time Watcher Started")

    return observer