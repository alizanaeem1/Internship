from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


persistent_directory = "db/chroma_db"


# Load HuggingFace embeddings
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# Load vector store
db = Chroma(
    persist_directory=persistent_directory,
    embedding_function=embedding_model,
    collection_metadata={"hnsw:space": "cosine"}
)


# Search for relevant documents
query = "How much did Microsoft pay to acquire GitHub?"


retriever = db.as_retriever(
    search_kwargs={"k": 3}
)


# Retrieve documents
relevant_docs = retriever.invoke(query)


print(f"User Query: {query}")


print("--- Context ---")

for i, doc in enumerate(relevant_docs, 1):
    print(f"Document {i}:\n{doc.page_content}\n")