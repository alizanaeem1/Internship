from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate


# Chroma database path
persistent_directory = "db/chroma_db"


# 1. Load embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# 2. Load existing vector database
db = Chroma(
    persist_directory=persistent_directory,
    embedding_function=embedding_model,
    collection_metadata={"hnsw:space": "cosine"}
)


# 3. Create retriever (top 3 chunks)
retriever = db.as_retriever(
    search_kwargs={
        "k": 3
    }
)


# 4. User query
query = "Who succeeded Ze'ev Drori as CEO in October 2008?"


# 5. Retrieve documents
docs = retriever.invoke(query)


print("\n--- Retrieved Documents ---")
 
for i, doc in enumerate(docs, 1):
    print(f"\nDocument {i}")
    print(doc.page_content)


# 6. Combine retrieved context

context = "\n\n".join(
    [doc.page_content for doc in docs]
)


prompt = PromptTemplate(
    template="""

You are a helpful assistant.

Answer the question using ONLY the given context.

Context:
{context}


Question:
{question}


Answer:

""",
    input_variables=[
        "context",
        "question"
    ]
)



# 7. Load Ollama model

llm = OllamaLLM(
    model="phi3"
)



# 8. Send context + question to LLM

final_prompt = prompt.format(
    context=context,
    question=query
)


response = llm.invoke(final_prompt)



# 9. Final answer

print("\n--- Final Answer ---")
print(response)