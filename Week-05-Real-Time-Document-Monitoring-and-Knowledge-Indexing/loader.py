from pathlib import Path
from PIL import Image
import pytesseract
import easyocr
reader = None

def get_reader():
    global reader

    if reader is None:
        reader = easyocr.Reader(['en'], gpu=False)

    return reader
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
)
from langchain_core.documents import Document
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".docx",
    ".png",
    ".jpg",
    ".jpeg",
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
            docs = loader.load()

        elif suffix == ".txt":
            loader = TextLoader(str(file), encoding="utf-8")
            docs = loader.load()

        elif suffix == ".docx":
            loader = Docx2txtLoader(str(file))
            docs = loader.load()

        elif suffix in [".png", ".jpg", ".jpeg"]:
            docs = load_image_document(file)

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
         encoding="utf-8",
         autodetect_encoding=True
        )

    elif suffix == ".docx":
        loader = Docx2txtLoader(str(file))

    elif suffix in [".png", ".jpg", ".jpeg"]:
        return load_image_document(file)

    else:
        return []

    return loader.load()


def load_image_document(file: Path) -> list[Document]:

    reader = get_reader()

    result = reader.readtext(str(file), detail=0)

    text = "\n".join(result)

    if not text.strip():
        return []

    return [
        Document(
            page_content=text,
            metadata={
                "source": str(file).lower(),
                "file_name": file.name.lower(),
            }
        )
    ]