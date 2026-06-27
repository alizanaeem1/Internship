from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL,
    DB_FOLDER,
    COLLECTION_NAME,
    SUPPORTED_FILES,
)

from loader import load_document
from utils import is_indexed, update_index, file_hash, remove_from_index


embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)

vector_store = Chroma(
    persist_directory=str(DB_FOLDER),
    embedding_function=embeddings,
    collection_name=COLLECTION_NAME,
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", " ", ""],
)


def delete_old_chunks(file: Path):
    source_path = str(file).lower()

    try:
        vector_store._collection.delete(
            where={"source": source_path}
        )
        print(f"✓ Old chunks deleted: {file.name}")

    except Exception as e:
        print(f"Delete warning: {e}")


def index_file(file: Path):

    if file.suffix.lower() not in SUPPORTED_FILES:
        return

    if is_indexed(file):
        print(f"✓ Skipping: {file.name}")
        return

    print(f"Indexing: {file.name}")

    delete_old_chunks(file)

    documents = load_document(file)

    if not documents:
        return

    chunks = splitter.split_documents(documents)

    current_hash = file_hash(file)

    for chunk in chunks:
        chunk.metadata["source"] = str(file).lower()
        chunk.metadata["file_hash"] = current_hash

    vector_store.add_documents(chunks)

    update_index(file)

    print(f"✓ Added {len(chunks)} chunks")


def delete_file_vectors(file: Path):
    source_path = str(file).lower()

    try:
        vector_store._collection.delete(
            where={"source": source_path}
        )
        print(f"✓ Deleted vectors: {file.name}")

    except Exception as e:
        print(f"Delete warning: {e}")

    remove_from_index(file)


def index_folder(folder: Path):

    print("\nScanning data folder...\n")

    total_files = 0

    for file in folder.iterdir():

        if not file.is_file():
            continue

        if file.suffix.lower() not in SUPPORTED_FILES:
            continue

        total_files += 1
        index_file(file)

    print("\n======================================")
    print(f"Total Supported Files : {total_files}")
    print("Database is up to date.")
    print("======================================")