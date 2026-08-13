from pathlib import Path
from dotenv import load_dotenv
import os

# =====================================
# Load Environment Variables
# =====================================

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Web Search (Currently Disabled)
# TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


# =====================================
# Project Paths
# =====================================

BASE_DIR = Path(__file__).parent

DATA_FOLDER = BASE_DIR / "data"
DB_FOLDER = BASE_DIR / "db"
LOG_FOLDER = BASE_DIR / "logs"

MEMORY_DB_FOLDER = BASE_DIR / "memory_db"

MEMORY_COLLECTION = "memory"
# =====================================
# Supported Files
# =====================================

SUPPORTED_FILES = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
    ".png",
    ".jpg",
    ".jpeg",
}


# =====================================
# Gemini
# =====================================

GEMINI_MODEL = "gemini-2.5-flash"


# =====================================
# Embedding Model
# =====================================

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = "realtime-rag"

PINECONE_HOST = "https://realtime-rag-yg09424.svc.aped-4627-b74a.pinecone.io"
# =====================================
# ChromaDB
# =====================================

COLLECTION_NAME = "documents"


# =====================================
# Chunking
# =====================================

# Best for Markdown + QHSE Dataset

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 250


# =====================================
# Metadata
# =====================================

INDEX_FILE = DB_FOLDER / "indexed_files.json"


# =====================================
# Retrieval
# =====================================

TOP_K = 8
FETCH_K = 20


# =====================================
# OCR
# =====================================

OCR_LANGUAGE = ["en"]


# =====================================
# Debug
# =====================================

DEBUG = False