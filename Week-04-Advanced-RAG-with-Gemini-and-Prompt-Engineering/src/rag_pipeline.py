"""
RAG Pipeline

Handles document retrieval from ChromaDB
and prepares context for Gemini.
"""

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from config.settings import TOP_K


class RAGPipeline:

    def __init__(self, db_path="db"):

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.vector_store = Chroma(
            persist_directory=db_path,
            embedding_function=self.embeddings
        )

        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": TOP_K}
        )

    def retrieve_documents(self, query):

        docs = self.retriever.invoke(query)

        return docs

    def build_context(self, documents):

        context = ""

        for doc in documents:

            context += doc.page_content

            context += "\n\n"

        return context.strip()