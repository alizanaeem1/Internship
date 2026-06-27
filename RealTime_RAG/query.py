from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from config import (
    DB_FOLDER,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    GOOGLE_API_KEY,
    GEMINI_MODEL,
)

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)

vector_db = Chroma(
    persist_directory=str(DB_FOLDER),
    embedding_function=embeddings,
    collection_name=COLLECTION_NAME,
)
print("Vector Count:", vector_db._collection.count())
retriever = vector_db.as_retriever(
    search_kwargs={"k": 5}
)

llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GOOGLE_API_KEY,
    temperature=0,
)

prompt = ChatPromptTemplate.from_template(
    """
You are a helpful AI assistant.

Answer ONLY from the provided context.

If the answer is not found in the context, say:

"I don't know based on the provided documents."

Context:
{context}

Question:
{question}
"""
)

def ask_question(question: str):

    docs = retriever.invoke(question)

    print("\nRetrieved Docs:", len(docs))

    for i, doc in enumerate(docs, start=1):
        print(f"\n===== Document {i} =====")
        print(doc.metadata)
        print(doc.page_content[:300])

    context = "\n\n".join(doc.page_content for doc in docs)

    print("\n================== CONTEXT ==================")
    print(context[:1000])
    print("=============================================\n")

    chain = prompt | llm

    response = chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )

    return response.content