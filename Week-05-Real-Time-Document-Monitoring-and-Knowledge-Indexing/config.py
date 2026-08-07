from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
# ==========================
# Project Paths
# ==========================
SUPPORTED_FILES = {
    ".pdf",
    ".txt",
    ".docx",
    ".png",
    ".jpg",
    ".jpeg",
}

BASE_DIR = Path(__file__).parent

DATA_FOLDER = BASE_DIR / "data"
DB_FOLDER = BASE_DIR / "db"
LOG_FOLDER = BASE_DIR / "logs"

# ==========================
# Google Gemini
# ==========================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

GEMINI_MODEL = "gemini-2.5-flash"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# ==========================
# Chroma
# ==========================

COLLECTION_NAME = "documents"

# ==========================
# Chunking
# ==========================

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# ==========================
# Metadata
# ==========================

INDEX_FILE = DB_FOLDER / "indexed_files.json"

