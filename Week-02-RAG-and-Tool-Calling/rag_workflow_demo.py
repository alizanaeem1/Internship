"""
Week 2 - RAG Workflow Demonstration

This program demonstrates the main steps of Retrieval-Augmented Generation:

1. Load documents
2. Split documents into chunks
3. Create simple vector representations
4. Compare the user query with document chunks
5. Retrieve the most relevant chunks
6. Generate an answer from the retrieved context

This educational version uses word-frequency vectors instead of an external
embedding model so that it can run without additional libraries.
"""

from collections import Counter
from math import sqrt
import re
from typing import Dict, List, Tuple


DOCUMENTS: Dict[str, str] = {
    "rag_overview": """
    Retrieval-Augmented Generation, commonly called RAG, combines information
    retrieval with a large language model. Before generating an answer, the
    system searches a knowledge base and retrieves relevant information.
    The retrieved information is added to the prompt as context.
    """,
    "embeddings": """
    Embeddings are numerical representations of text. They capture semantic
    meaning and allow similar pieces of text to be compared. In a RAG system,
    document chunks and user queries are converted into embeddings.
    """,
    "vector_database": """
    A vector database stores embeddings and their related documents.
    It supports similarity search so that the system can find chunks that are
    semantically related to the user query.
    """,
    "chunking": """
    Chunking means dividing a large document into smaller text sections.
    Proper chunking improves retrieval accuracy because the system searches
    focused pieces of information instead of entire documents.
    """,
    "generation": """
    After relevant chunks are retrieved, they are passed to a language model.
    The model uses the provided context to generate an accurate and grounded
    response. If the answer is not present in the context, the system should
    avoid guessing.
    """,
}


def normalize_text(text: str) -> List[str]:
    """Convert text to lowercase words and remove punctuation."""
    return re.findall(r"[a-zA-Z]+", text.lower())


def split_into_chunks(text: str, chunk_size: int = 28) -> List[str]:
    """Split text into fixed-size word chunks."""
    words = text.split()
    return [
        " ".join(words[index:index + chunk_size])
        for index in range(0, len(words), chunk_size)
    ]


def create_vector(text: str) -> Counter:
    """Create a simple word-frequency vector."""
    return Counter(normalize_text(text))


def cosine_similarity(first_vector: Counter, second_vector: Counter) -> float:
    """Calculate cosine similarity between two word-frequency vectors."""
    common_words = set(first_vector) & set(second_vector)

    dot_product = sum(
        first_vector[word] * second_vector[word]
        for word in common_words
    )

    first_magnitude = sqrt(
        sum(value ** 2 for value in first_vector.values())
    )
    second_magnitude = sqrt(
        sum(value ** 2 for value in second_vector.values())
    )

    if first_magnitude == 0 or second_magnitude == 0:
        return 0.0

    return dot_product / (first_magnitude * second_magnitude)


def build_knowledge_base(
    documents: Dict[str, str]
) -> List[Dict[str, object]]:
    """Split documents into chunks and store their vectors."""
    knowledge_base = []

    for document_name, document_text in documents.items():
        chunks = split_into_chunks(document_text)

        for chunk_number, chunk in enumerate(chunks, start=1):
            knowledge_base.append(
                {
                    "document": document_name,
                    "chunk_number": chunk_number,
                    "text": chunk.strip(),
                    "vector": create_vector(chunk),
                }
            )

    return knowledge_base


def retrieve_relevant_chunks(
    query: str,
    knowledge_base: List[Dict[str, object]],
    top_k: int = 3,
) -> List[Tuple[float, Dict[str, object]]]:
    """Return the most relevant chunks for a user query."""
    query_vector = create_vector(query)
    scored_chunks = []

    for chunk in knowledge_base:
        score = cosine_similarity(query_vector, chunk["vector"])
        scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda item: item[0], reverse=True)

    return [
        item for item in scored_chunks[:top_k]
        if item[0] > 0
    ]


def generate_answer(
    query: str,
    retrieved_chunks: List[Tuple[float, Dict[str, object]]],
) -> str:
    """
    Generate a simple grounded answer.

    A real RAG system would send the query and retrieved context to an LLM.
    This demonstration returns the retrieved information directly.
    """
    if not retrieved_chunks:
        return (
            "The answer is not available in the current knowledge base."
        )

    context = " ".join(
        chunk["text"] for _, chunk in retrieved_chunks
    )

    return (
        f"Question: {query}\n\n"
        f"Retrieved Context:\n{context}\n\n"
        "Answer:\n"
        "Based on the retrieved knowledge, "
        f"{context}"
    )


def display_retrieval_results(
    results: List[Tuple[float, Dict[str, object]]]
) -> None:
    """Display retrieved chunks and similarity scores."""
    print("\nRetrieved Chunks")
    print("-" * 60)

    if not results:
        print("No relevant chunks found.")
        return

    for position, (score, chunk) in enumerate(results, start=1):
        print(f"\nResult {position}")
        print(f"Document: {chunk['document']}")
        print(f"Chunk: {chunk['chunk_number']}")
        print(f"Similarity Score: {score:.3f}")
        print(f"Text: {chunk['text']}")


def run_demo() -> None:
    """Run sample RAG queries."""
    knowledge_base = build_knowledge_base(DOCUMENTS)

    sample_queries = [
        "What is RAG?",
        "Why are embeddings used?",
        "What does a vector database do?",
        "Why should documents be divided into chunks?",
        "Who invented Python?",
    ]

    print("RAG WORKFLOW DEMONSTRATION")
    print("=" * 60)
    print(f"Documents Loaded: {len(DOCUMENTS)}")
    print(f"Chunks Created: {len(knowledge_base)}")

    for query in sample_queries:
        print("\n" + "=" * 60)
        print("User Query:", query)

        results = retrieve_relevant_chunks(
            query=query,
            knowledge_base=knowledge_base,
            top_k=2,
        )

        display_retrieval_results(results)
        print("\n" + generate_answer(query, results))


if __name__ == "__main__":
    run_demo()
