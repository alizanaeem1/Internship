from pathlib import Path
from datetime import date, datetime

import yaml
import easyocr

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
)
from langchain_core.documents import Document


reader = None


SUPPORTED_EXTENSIONS = [
    ".pdf",
    ".docx",
    ".txt",
    ".md",
    ".png",
    ".jpg",
    ".jpeg",
]


def sanitize_metadata(metadata: dict) -> dict:
    clean = {}

    for key, value in metadata.items():
        if isinstance(value, (date, datetime)):
            clean[key] = value.isoformat()

        elif isinstance(value, (str, int, float, bool)) or value is None:
            clean[key] = value

        elif isinstance(value, list):
            clean[key] = [
                item.isoformat()
                if isinstance(item, (date, datetime))
                else str(item)
                for item in value
            ]

        else:
            clean[key] = str(value)

    return clean


def load_markdown_document(file: Path) -> list[Document]:
    try:
        text = file.read_text(encoding="utf-8-sig")
        text = text.lstrip("\ufeff")

        metadata = {
            "source": str(file).lower(),
            "file_name": file.name.lower(),
            "file_type": file.suffix.lower(),
        }

        content = text

        if text.startswith("---"):
            parts = text.split("---", 2)

            if len(parts) == 3:
                yaml_text = parts[1].strip()
                content = parts[2].strip()

                parsed_metadata = yaml.safe_load(yaml_text)

                if isinstance(parsed_metadata, dict):
                    metadata.update(
                        sanitize_metadata(parsed_metadata)
                    )

        if not content.strip():
            return []

        return [
            Document(
                page_content=content,
                metadata=metadata,
            )
        ]

    except Exception as e:
      print(
        f"⚠ Failed to load Markdown {file.name}: "
        f"{type(e).__name__}: {e}"
      )
    return []

def get_reader():
    global reader

    if reader is None:
        reader = easyocr.Reader(["en"], gpu=False)

    return reader


def load_documents(data_folder: Path) -> list[Document]:
    documents = []

    for file in data_folder.rglob("*"):
        if not file.is_file():
            continue

        if file.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        docs = load_document(file)

        if docs:
            documents.extend(docs)

    return documents


def load_document(file: Path) -> list[Document]:
    suffix = file.suffix.lower()

    try:
        if suffix == ".pdf":
            loader = PyPDFLoader(str(file))
            return loader.load()

        elif suffix == ".txt":
            loader = TextLoader(
                str(file),
                encoding="utf-8",
                autodetect_encoding=True,
            )
            return loader.load()

        elif suffix == ".md":
            return load_markdown_document(file)

        elif suffix == ".docx":
            loader = Docx2txtLoader(str(file))
            return loader.load()

        elif suffix in [".png", ".jpg", ".jpeg"]:
            return load_image_document(file)

        return []

    except Exception as e:
        print(f"⚠ Failed to load {file.name}: {e}")
        return []


def load_image_document(file: Path) -> list[Document]:
    try:
        image_reader = get_reader()
        result = image_reader.readtext(str(file), detail=0)

        text = "\n".join(result)

        if not text.strip():
            return []

        return [
            Document(
                page_content=text,
                metadata={
                    "source": str(file).lower(),
                    "file_name": file.name.lower(),
                    "file_type": file.suffix.lower(),
                },
            )
        ]

    except Exception as e:
        print(f"⚠ OCR failed for {file.name}: {e}")
        return []