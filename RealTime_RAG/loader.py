from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
)
from langchain_core.documents import Document


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".docx",
}


def load_documents(data_folder: Path) -> list[Document]:
    """
    Load all supported documents from the data folder.
    """

    documents = []

    for file in data_folder.iterdir():

        if not file.is_file():
            continue

        suffix = file.suffix.lower()

        if suffix not in SUPPORTED_EXTENSIONS:
            print(f"Skipping: {file.name}")
            continue

        print(f"Loading: {file.name}")

        if suffix == ".pdf":
            loader = PyPDFLoader(str(file))

        elif suffix == ".txt":
            loader = TextLoader(str(file), encoding="utf-8")

        elif suffix == ".docx":
            loader = Docx2txtLoader(str(file))

        docs = loader.load()

        documents.extend(docs)

    return documents
def load_document(file: Path) -> list[Document]:
    """
    Load a single document.
    """

    suffix = file.suffix.lower()

    if suffix == ".pdf":
        loader = PyPDFLoader(str(file))

    elif suffix == ".txt":
        loader = TextLoader(
            str(file),
            encoding="utf-8"
        )

    elif suffix == ".docx":
        loader = Docx2txtLoader(str(file))

    else:
        return []

    return loader.load()
def load_document(file: Path) -> list[Document]:
    """
    Load a single document.
    """

    suffix = file.suffix.lower()

    if suffix == ".pdf":
        loader = PyPDFLoader(str(file))

    elif suffix == ".txt":
        loader = TextLoader(
            str(file),
            encoding="utf-8"
        )

    elif suffix == ".docx":
        loader = Docx2txtLoader(str(file))

    else:
        return []

    return loader.load()