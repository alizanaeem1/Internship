# Week 5 – Real-Time Document Monitoring and Knowledge Indexing

## Overview

During the fifth week of my internship, I focused on developing a real-time document monitoring and knowledge indexing system to enhance the Retrieval-Augmented Generation (RAG) pipeline. The system automatically detects newly added documents, extracts their content, generates embeddings, and updates the vector database without rebuilding the entire knowledge base.

The application supports multiple document formats, including PDF, Microsoft Word (DOCX), Text (TXT), and image files (PNG, JPG, and JPEG). Images are processed using OCR to extract text before indexing. Once indexed, the documents can be retrieved through semantic search and used by Google Gemini to generate accurate, context-aware responses.

---

# Objectives

- Develop a real-time document monitoring system.
- Automatically detect and process newly added documents.
- Implement incremental knowledge indexing.
- Support multiple document formats.
- Extract text from images using OCR.
- Generate embeddings and update ChromaDB automatically.
- Improve retrieval speed and efficiency.

---

# Features

- Real-Time Document Monitoring
- Automatic File Detection
- Incremental Knowledge Indexing
- Google Gemini Integration
- ChromaDB Vector Database
- Semantic Search
- OCR-Based Image Text Extraction
- PDF (.pdf) Support
- Microsoft Word (.docx) Support
- Text (.txt) Support
- Image Support (.png, .jpg, .jpeg)
- Automatic Embedding Generation
- Modular Python Architecture
- Logging and Error Handling

---

# Technologies Used

- Python
- Google Gemini API
- LangChain
- ChromaDB
- HuggingFace Embeddings
- EasyOCR
- PyMuPDF
- python-docx
- Watchdog
- python-dotenv
- Git & GitHub
- Visual Studio Code

---

# Project Structure

```text
Week-05-Real-Time-Document-Monitoring-and-Knowledge-Indexing/
│
├── .env.example
├── config.py
├── indexer_old.py
├── ingest.py
├── loader.py
├── main.py
├── query.py
├── requirements.txt
├── utils.py
└── watcher.py
```

---

# File Description

### main.py

The main entry point of the application. It initializes the system, starts document monitoring, and coordinates the indexing and retrieval workflow.

### watcher.py

Continuously monitors the document directory and automatically detects newly added files for processing.

### loader.py

Loads and extracts text from supported file formats:

- PDF (.pdf)
- Microsoft Word (.docx)
- Text (.txt)
- Images (.png, .jpg, .jpeg)

Images are processed using OCR to convert text from images into searchable content.

### ingest.py

Processes extracted text, splits it into chunks, generates embeddings, and stores them in the ChromaDB vector database.

### query.py

Retrieves the most relevant document chunks using semantic search and prepares the context for response generation.

### config.py

Contains project configuration, environment variables, model settings, and application paths.

### utils.py

Provides reusable helper functions for logging, preprocessing, and utility operations.

### indexer_old.py

Stores the previous indexing implementation used during development before introducing the real-time indexing workflow.

---

# System Workflow

```text
New Document
      │
      ▼
Folder Monitoring (Watchdog)
      │
      ▼
Document Loader
      │
      ▼
Text Extraction
(PDF / DOCX / TXT / OCR Images)
      │
      ▼
Text Chunking
      │
      ▼
Embedding Generation
      │
      ▼
ChromaDB Vector Database
      │
      ▼
Semantic Search
      │
      ▼
Google Gemini
      │
      ▼
Context-Aware Response
```

---

# Learning Outcomes

By the end of this week, I was able to:

- Build a real-time document monitoring system.
- Process PDF, DOCX, TXT, and image files.
- Extract text from images using OCR.
- Generate vector embeddings using HuggingFace models.
- Store and manage document embeddings in ChromaDB.
- Implement incremental knowledge indexing.
- Perform semantic document retrieval.
- Integrate Google Gemini with a continuously updated knowledge base.
- Improve the scalability and efficiency of AI-powered document retrieval systems.

---

# Challenges Faced

- Monitoring directories efficiently for newly added files.
- Processing multiple document formats.
- Extracting text accurately from image files.
- Preventing duplicate document indexing.
- Updating the vector database without rebuilding it.
- Maintaining efficient semantic retrieval as the knowledge base grows.

---

# Solutions Implemented

- Implemented automatic folder monitoring using Watchdog.
- Used OCR for extracting text from image files.
- Applied incremental indexing to update the vector database.
- Organized the application into modular Python components.
- Used ChromaDB for efficient semantic retrieval.
- Improved code maintainability through reusable utility functions.

---

# Future Improvements

- Support additional document formats.
- Synchronize document deletion with the vector database.
- Add conversation memory for multi-turn interactions.
- Implement metadata-based filtering.
- Improve embedding performance for large datasets.
- Deploy the system as a web-based AI assistant.

---

# Conclusion

This week focused on building a real-time document processing and knowledge indexing system capable of automatically monitoring, processing, and indexing documents from multiple sources. By integrating OCR, ChromaDB, semantic retrieval, and Google Gemini, the application became more efficient, scalable, and suitable for real-world AI-powered knowledge management systems.