# Week 2 – Understanding RAG and Tool Calling

## Overview

During the second week of the internship, I studied Retrieval-Augmented Generation (RAG) and tool calling. The main objective was to understand how an AI system can retrieve relevant information from a knowledge base and use external tools when the required information is not directly available.

## Topics Covered

- Retrieval-Augmented Generation (RAG)
- Document loading and text chunking
- Text embeddings
- Vector databases
- Similarity search
- Context-based response generation
- Tool calling
- Tool selection
- Function execution
- Combining RAG with tools

## Files Included

1. `rag_workflow_demo.py`
   - Demonstrates document loading
   - Splits text into chunks
   - Creates simple vector representations
   - Retrieves relevant chunks
   - Generates a context-based answer

2. `tool_calling_demo.py`
   - Demonstrates tool registration
   - Detects user intent
   - Selects the correct tool
   - Executes calculator, date, and search tools

3. `rag_with_tool_calling.py`
   - Combines document retrieval with tool calling
   - Uses RAG for knowledge-base questions
   - Uses tools for calculations and external information
   - Includes an out-of-context response

## Tools and Technologies Used

- Python
- Visual Studio Code
- Git
- GitHub
- RAG concepts
- Tool-calling concepts

## Learning Outcomes

- Understood the complete RAG workflow.
- Learned how text is converted into chunks and searchable representations.
- Understood how relevant context is retrieved for a user query.
- Learned how an AI system selects and executes tools.
- Understood when to use retrieved documents and when to call an external tool.
- Practiced combining RAG and tool calling in a single workflow.

## Work Completed

- Created a basic RAG simulation in Python.
- Implemented a simple tool-calling framework.
- Built a combined RAG and tool-calling assistant.
- Tested document questions, calculations, date queries, and out-of-context handling.

## How to Run

```bash
python rag_workflow_demo.py
python tool_calling_demo.py
python rag_with_tool_calling.py
```

These examples use only the Python standard library, so no additional packages are required.
