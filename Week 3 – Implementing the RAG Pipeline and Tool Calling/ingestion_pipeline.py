import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma


def load_documents(docs_path="docs"):
    """Load all text files from the docs directory"""

    print(f"Loading documents from {docs_path}...")

    if not os.path.exists(docs_path):
        raise FileNotFoundError(
            f"The directory '{docs_path}' does not exist. Please create it and add your text files."
        )

    loader = DirectoryLoader(
        path=docs_path,
    glob="*.txt",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"}
    )

    documents = loader.load()

    if len(documents) == 0:
        raise FileNotFoundError(
            f"No .txt files found in '{docs_path}'."
        )

    print(f"\nLoaded {len(documents)} documents")

    for i, doc in enumerate(documents[:2]):
        print(f"\nDocument {i+1}")
        print(f"Source: {doc.metadata['source']}")
        print(f"Length: {len(doc.page_content)} characters")
        print(f"Preview: {doc.page_content[:100]}...")

    return documents


def split_documents(documents, chunk_size=1000, chunk_overlap=100):
    """Split documents into chunks"""

    print("\nSplitting documents into chunks...")

    text_splitter = CharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = text_splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks")

    for i, chunk in enumerate(chunks[:5]):
        print(f"\n--- Chunk {i+1} ---")
        print(f"Source: {chunk.metadata['source']}")
        print(f"Length: {len(chunk.page_content)}")
        print(chunk.page_content[:200])
        print("-" * 50)

    return chunks


def create_vector_store(chunks, persist_directory="db/chroma_db"):
    """Create ChromaDB vector store"""

    print("\nLoading embedding model...")

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("Creating vector store...")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=persist_directory
    )

    print("Vector store created successfully!")

    return vectorstore


def main():

    print("=== RAG Document Ingestion Pipeline ===\n")

    docs_path = "docs"
    persist_directory = "db/chroma_db"

    if os.path.exists(persist_directory):

        print("Vector database already exists.")

        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model
        )

        print(
            f"Loaded existing vector store with {vectorstore._collection.count()} chunks"
        )

        return vectorstore

    print("Creating new vector database...\n")

    documents = load_documents(docs_path)

    chunks = split_documents(documents)

    vectorstore = create_vector_store(
        chunks,
        persist_directory
    )

    print("\n✅ Ingestion completed successfully!")

    return vectorstore


if __name__ == "__main__":
    main()