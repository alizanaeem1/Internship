from pathlib import Path
import time
import threading
from utils import is_indexed
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import DATA_FOLDER, SUPPORTED_FILES
from config import DATA_FOLDER
from ingest import index_file, delete_file_vectors


DEBOUNCE_SECONDS = 3
timers = {}


def show_prompt():
    print("\n>>> ", end="", flush=True)


def is_temp_file(path: str):
    name = Path(path).name.lower()

    return (
        name.startswith("~$")
        or name.startswith("~wrd")
        or name.startswith("~wrl")
        or name.endswith(".tmp")
    )


def safe_index(file_path: str):
    if is_temp_file(file_path):
        return

    file = Path(file_path)

    if not file.exists():
     return

    if file.suffix.lower() not in SUPPORTED_FILES:
     return

    print(f"\n📄 Processing: {file.name}")
    print("⏳ Waiting for file to finish saving...")

    time.sleep(1)

    print(f"📥 Indexing {file.name}...")

    for attempt in range(5):
        try:
            index_file(file, force=True)
            break

        except PermissionError:
            print(f"\n⚠ File locked, retrying... {attempt + 1}/5")
            time.sleep(2)

        except FileNotFoundError:
            return

        except Exception as e:
            print(f"\n❌ Watcher error: {e}")
            break

    show_prompt()


def debounce_index(file_path: str):
    if is_temp_file(file_path):
        return

    if file_path in timers:
        timers[file_path].cancel()

    timer = threading.Timer(
        DEBOUNCE_SECONDS,
        safe_index,
        args=(file_path,)
    )

    timers[file_path] = timer
    timer.start()


class DocumentWatcher(FileSystemEventHandler):

    def on_created(self, event):
        if event.is_directory or is_temp_file(event.src_path):
            return

        debounce_index(event.src_path)

    def on_modified(self, event):
        if event.is_directory or is_temp_file(event.src_path):
            return

        debounce_index(event.src_path)

    def on_deleted(self, event):
        if event.is_directory or is_temp_file(event.src_path):
            return

        file_path = event.src_path

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
    observer = Observer()

    observer.schedule(
        DocumentWatcher(),
        str(DATA_FOLDER),
        recursive=False,
    )

    observer.start()

    print("✅ Real-Time Watcher Started")

    return observer