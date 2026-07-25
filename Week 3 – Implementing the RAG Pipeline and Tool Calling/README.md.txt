# Week 3 – Implementing the RAG Pipeline and Tool Calling

## Overview

During the third week of my internship, I started implementing the core components of the Retrieval-Augmented Generation (RAG) system. The focus was on building the document ingestion pipeline, retrieval pipeline, response generation module, and integrating multiple tools to enhance the AI assistant's capabilities.

---

## Tasks Performed

### RAG Implementation

- Developed the document ingestion pipeline.
- Processed documents before indexing.
- Generated vector embeddings for documents.
- Stored embeddings in ChromaDB.
- Implemented the retrieval pipeline for semantic search.
- Retrieved the most relevant document chunks based on user queries.
- Connected the retrieval pipeline with the response generation module.

### Tool Calling Implementation

- Developed a tool-calling demonstration.
- Implemented multiple utility tools:
  - Weather Tool
  - Currency Tool
  - Time Tool
- Designed the workflow for selecting the appropriate tool based on user queries.
- Tested tool execution and response generation.

---

## Learning Outcomes

By the end of this week, I was able to:

- Build a complete document ingestion workflow.
- Understand document indexing in a vector database.
- Retrieve relevant information using semantic search.
- Generate responses using retrieved context.
- Implement modular Python tools.
- Understand how AI assistants integrate external tools with RAG systems.

---

## Technologies Used

- Python
- LangChain
- ChromaDB
- HuggingFace Embeddings
- Sentence Transformers (all-MiniLM-L6-v2)
- Visual Studio Code
- Git
- GitHub

---

## Project Structure

```
Week-03/
│
├── docs/
├── db/
├── ingestion_pipeline.py
├── retrieval_pipeline.py
├── answer_generate.py
├── tool_demo.py
├── weather_tool.py
├── currency_tool.py
├── time_tool.py
└── .env
```

---

## Work Completed

- Implemented the document ingestion pipeline.
- Created the semantic retrieval pipeline.
- Connected retrieval with answer generation.
- Integrated multiple utility tools.
- Tested RAG retrieval using different user queries.
- Verified tool execution for weather, currency, and time-related requests.

---

## Repository Contents

| File | Description |
|------|-------------|
| `ingestion_pipeline.py` | Processes documents and stores embeddings in the vector database. |
| `retrieval_pipeline.py` | Retrieves relevant document chunks using semantic similarity search. |
| `answer_generate.py` | Generates responses using the retrieved context. |
| `tool_demo.py` | Demonstrates the tool-calling workflow. |
| `weather_tool.py` | Provides weather-related information. |
| `currency_tool.py` | Performs currency conversion. |
| `time_tool.py` | Returns the current date and time. |
| `docs/` | Contains source documents used for indexing. |
| `db/` | Stores the ChromaDB vector database. |

---

## Conclusion

This week focused on the practical implementation of the RAG pipeline and Tool Calling. By integrating document retrieval with external tools, I gained hands-on experience in building the foundation of an intelligent AI assistant capable of retrieving knowledge and executing specialized functions.