from pathlib import Path
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from config import DB_FOLDER, COLLECTION_NAME, EMBEDDING_MODEL

file = Path("data/QHSE/03_Quality/04_QA_vs_QC.md").resolve()
source = str(file).lower()

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

vectorstore = Chroma(
    persist_directory=str(DB_FOLDER),
    embedding_function=embeddings,
    collection_name=COLLECTION_NAME,
)

results = vectorstore.get(where={"source": source})

print("Source:", source)
print("Chunks found:", len(results["ids"]))

if results["ids"]:
    print(results["documents"][0][:500])