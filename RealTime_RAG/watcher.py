from pathlib import Path
import time
import threading

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from config import DATA_FOLDER
from ingest import index_file, delete_file_vectors


def show_prompt():
    print("\n>>> ", end="", flush=True)


def safe_index(file_path: str):
    file = Path(file_path)

    time.sleep(2)

    for attempt in range(5):
        try:
            index_file(file)
            break

        except PermissionError:
            print(f"\nFile locked, retrying... {attempt + 1}/5")
            time.sleep(2)

        except Exception as e:
            print(f"\nWatcher error: {e}")
            break

    show_prompt()


class DocumentWatcher(FileSystemEventHandler):

    def on_created(self, event):
        if event.is_directory:
            return

        print(f"\nNew File Detected: {event.src_path}")

        threading.Thread(
            target=safe_index,
            args=(event.src_path,),
            daemon=True
        ).start()

    def on_modified(self, event):
        if event.is_directory:
            return

        print(f"\nModified File: {event.src_path}")

        threading.Thread(
            target=safe_index,
            args=(event.src_path,),
            daemon=True
        ).start()

    def on_deleted(self, event):
        if event.is_directory:
            return

        file = Path(event.src_path)

        print(f"\nFile Deleted: {event.src_path}")

        delete_file_vectors(file)

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