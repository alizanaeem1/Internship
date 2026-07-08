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
    separators=["\n\n", "\n", ".", " ", ""],
)


def normalize_text(text: str) -> str:
    return " ".join(text.split())


def delete_old_chunks(file: Path):
    source_path = str(file).lower()

    try:
        vector_store._collection.delete(
            where={"source": source_path}
        )
        # print(f"✓ Old chunks deleted: {file.name}")

    except Exception as e:
        print(f"Delete warning: {e}")


def remove_duplicate_chunks(chunks):
    unique_chunks = []
    seen = set()

    for chunk in chunks:
        text = normalize_text(chunk.page_content).lower()

        if text in seen:
            continue

        seen.add(text)
        unique_chunks.append(chunk)

    return unique_chunks


def index_file(file: Path, force: bool = False):

    if file.suffix.lower() not in SUPPORTED_FILES:
        return

    if is_indexed(file) and not force:
        print(f"✓ Skipping: {file.name}")
        return

    # print(f"Indexing: {file.name}")

    delete_old_chunks(file)

    documents = load_document(file)

    if not documents:
        print(f"⚠ No content loaded from: {file.name}")
        return

    for doc in documents:
        doc.page_content = normalize_text(doc.page_content)

    chunks = splitter.split_documents(documents)

    chunks = remove_duplicate_chunks(chunks)

    current_hash = file_hash(file)

    for chunk in chunks:
        chunk.metadata["source"] = str(file).lower()
        chunk.metadata["file_hash"] = current_hash
        chunk.metadata["file_name"] = file.name.lower()

    vector_store.add_documents(chunks)

    update_index(file)

    # print(f"✓ Added {len(chunks)} unique chunks")


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


def index_folder(folder: Path, force: bool = False):

    print("\nScanning data folder...\n")

    total_files = 0

    for file in folder.iterdir():

        if not file.is_file():
            continue

        if file.suffix.lower() not in SUPPORTED_FILES:
            continue

        total_files += 1
        index_file(file, force=force)

    print("\n======================================")
    print(f"Total Supported Files : {total_files}")
    print("Database is up to date.")
    print("======================================")