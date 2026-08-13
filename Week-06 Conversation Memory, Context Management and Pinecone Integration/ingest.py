from pathlib import Path

from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL,
   PINECONE_API_KEY,
   PINECONE_INDEX,
    SUPPORTED_FILES,
)

from loader import load_document
from utils import is_indexed, update_index, file_hash, remove_from_index


embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)


pc = Pinecone(api_key=PINECONE_API_KEY)

index = pc.Index(PINECONE_INDEX)

vector_store = PineconeVectorStore(
    index=index,
    embedding=embeddings,
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=[
        "\n# ",
        "\n## ",
        "\n### ",
        "\n\n",
        "\n",
        ". ",
        " ",
        "",
    ],
)


def normalize_text(text: str) -> str:
    lines = []

    for line in text.splitlines():
        cleaned_line = " ".join(line.split())
        lines.append(cleaned_line)

    return "\n".join(lines).strip()


def get_category(file: Path) -> str:
    parent = file.parent.name

    if "_" in parent:
        parent = parent.split("_", 1)[1]

    return parent.replace("_", " ").title()


def get_title(file: Path, documents=None) -> str:
    if documents:
        for doc in documents:
            for line in doc.page_content.splitlines():
                line = line.strip()
                if line.startswith("# "):
                    return line.replace("#", "").strip()

    title = file.stem

    if "_" in title:
        parts = title.split("_")
        if parts[0].isdigit():
            title = "_".join(parts[1:])

    return title.replace("_", " ").title()

def get_domain(file: Path) -> str:
    path_lower = str(file).lower()

    if "dot" in path_lower:
        return "DOT Compliance"

    if "qhse" in path_lower:
        return "QHSE"

    return "Unknown"


def get_subcategory(file: Path) -> str:
    folder_name = file.parent.name

    if "_" in folder_name:
        first, remaining = folder_name.split("_", 1)

        if first.isdigit():
            folder_name = remaining

    return folder_name.replace("_", " ").title()


def get_document_id(file: Path, documents=None) -> str:
    if documents:
        for doc in documents:
            document_id = doc.metadata.get("document_id")

            if document_id:
                return str(document_id)

    return file.stem.upper().replace("_", "-").replace(" ", "-")


def delete_old_chunks(file: Path):
    """
    Temporary disabled.
    Pinecone delete will be added later.
    """
    pass

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

    delete_old_chunks(file)

    documents = load_document(file)

    if not documents:
        print(f"⚠ No content loaded from: {file.name}")
        return

   

    if not documents:
        print(f"⚠ No content loaded from: {file.name}")
        return

    current_hash = file_hash(file)
    category = get_category(file)
    title = get_title(file, documents)

    # New metadata fields
    domain = get_domain(file)
    subcategory = get_subcategory(file)
    document_id = get_document_id(file, documents)

    # ---------- Prepare Documents ----------
    for doc in documents:
        clean_content = normalize_text(doc.page_content)

        doc.page_content = (
            f"Domain: {domain}\n"
            f"Category: {category}\n"
            f"Subcategory: {subcategory}\n"
            f"Title: {title}\n"
            f"Document ID: {document_id}\n"
            f"File Name: {file.name}\n"
            f"Topic: {title}\n\n"
            f"{clean_content}"
        )

        doc.metadata["source"] = str(file).lower()
        doc.metadata["file_hash"] = current_hash
        doc.metadata["file_name"] = file.name.lower()
        doc.metadata["domain"] = domain
        doc.metadata["category"] = category
        doc.metadata["subcategory"] = subcategory
        doc.metadata["document_id"] = document_id
        doc.metadata["title"] = title
        doc.metadata["file_type"] = file.suffix.lower()

    chunks = splitter.split_documents(documents)
    filtered_chunks = []

    for chunk in chunks:
        text = chunk.page_content.strip()

        # Skip metadata-only chunks
        if len(text) < 100:
            continue

        if text.startswith("Domain:") and "##" not in text:
            continue

        filtered_chunks.append(chunk)

    chunks = filtered_chunks
    chunks = remove_duplicate_chunks(chunks)

   

    # ---------- Chunk Metadata ----------
    for chunk in chunks:
        chunk.metadata["source"] = str(file).lower()
        chunk.metadata["file_hash"] = current_hash
        chunk.metadata["file_name"] = file.name.lower()
        chunk.metadata["domain"] = domain
        chunk.metadata["category"] = category
        chunk.metadata["subcategory"] = subcategory
        chunk.metadata["document_id"] = document_id
        chunk.metadata["title"] = title
        chunk.metadata["file_type"] = file.suffix.lower()

    vector_store.add_documents(chunks)
    update_index(file)

def delete_file_vectors(file: Path):
    """
    Temporary disabled.
    Pinecone delete will be added later.
    """
    remove_from_index(file)


def index_folder(folder: Path, force: bool = False):
    print("\nScanning data folder...\n")

    total_files = 0

    for file in folder.rglob("*"):
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

from config import DATA_FOLDER

if __name__ == "__main__":
    index_folder(Path(DATA_FOLDER))