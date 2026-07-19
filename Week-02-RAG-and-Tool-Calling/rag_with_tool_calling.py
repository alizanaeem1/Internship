"""
Week 2 - Combining RAG with Tool Calling

This program demonstrates a simple decision workflow:

1. Check whether a query requires a tool.
2. If a tool is required, call the relevant function.
3. Otherwise, search the local RAG knowledge base.
4. Return an out-of-context message when no answer is found.

This is a simplified educational example.
"""

from collections import Counter
from datetime import datetime
from math import sqrt
from typing import Callable, Dict, List, Tuple
import ast
import operator
import re


# ---------------------------------------------------------
# 1. KNOWLEDGE BASE
# ---------------------------------------------------------

KNOWLEDGE_BASE = {
    "rag": (
        "Retrieval-Augmented Generation retrieves relevant information "
        "from a knowledge base before generating an answer."
    ),
    "tool_calling": (
        "Tool calling allows a language model to choose and execute "
        "external functions such as calculators, search tools, or APIs."
    ),
    "chunking": (
        "Chunking divides large documents into smaller sections so that "
        "retrieval can return focused and relevant information."
    ),
    "embeddings": (
        "Embeddings convert text into numerical vectors that represent "
        "semantic meaning."
    ),
    "vector_database": (
        "A vector database stores document embeddings and supports "
        "similarity search."
    ),
}


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z]+", text.lower())


def vectorize(text: str) -> Counter:
    return Counter(tokenize(text))


def cosine_similarity(first: Counter, second: Counter) -> float:
    common_words = set(first) & set(second)

    dot_product = sum(
        first[word] * second[word]
        for word in common_words
    )

    first_length = sqrt(sum(value ** 2 for value in first.values()))
    second_length = sqrt(sum(value ** 2 for value in second.values()))

    if first_length == 0 or second_length == 0:
        return 0.0

    return dot_product / (first_length * second_length)


def retrieve_context(
    query: str,
    top_k: int = 2,
) -> List[Tuple[float, str, str]]:
    query_vector = vectorize(query)
    results = []

    for topic, content in KNOWLEDGE_BASE.items():
        combined_text = f"{topic} {content}"
        score = cosine_similarity(
            query_vector,
            vectorize(combined_text),
        )
        results.append((score, topic, content))

    results.sort(key=lambda item: item[0], reverse=True)

    return [
        result for result in results[:top_k]
        if result[0] > 0.05
    ]


# ---------------------------------------------------------
# 2. TOOLS
# ---------------------------------------------------------

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def evaluate_math(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
        return ALLOWED_OPERATORS[type(node.op)](
            evaluate_math(node.left),
            evaluate_math(node.right),
        )

    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPERATORS:
        return ALLOWED_OPERATORS[type(node.op)](
            evaluate_math(node.operand)
        )

    raise ValueError("Unsupported expression.")


def calculator(expression: str) -> str:
    try:
        parsed = ast.parse(expression, mode="eval")
        answer = evaluate_math(parsed.body)
        return f"The calculated result is {answer}."
    except (SyntaxError, ValueError, ZeroDivisionError) as error:
        return f"Unable to calculate the expression: {error}"


def current_date(_: str = "") -> str:
    return datetime.now().strftime(
        "Today is %A, %d %B %Y."
    )


TOOLS: Dict[str, Callable[[str], str]] = {
    "calculator": calculator,
    "current_date": current_date,
}


# ---------------------------------------------------------
# 3. ROUTING LOGIC
# ---------------------------------------------------------

def extract_expression(query: str) -> str:
    matches = re.findall(r"[0-9+\-*/().%\s]+", query)

    if not matches:
        return ""

    return max(matches, key=len).strip()


def detect_tool(query: str) -> str:
    normalized_query = query.lower()

    if any(
        keyword in normalized_query
        for keyword in ["today", "date", "current day"]
    ):
        return "current_date"

    expression = extract_expression(query)
    if expression and any(symbol in expression for symbol in "+-*/%"):
        return "calculator"

    return "none"


# ---------------------------------------------------------
# 4. RESPONSE GENERATION
# ---------------------------------------------------------

def answer_from_context(
    query: str,
    retrieved_context: List[Tuple[float, str, str]],
) -> str:
    if not retrieved_context:
        return (
            "Sorry, this information is not available in the current "
            "knowledge base."
        )

    context_text = " ".join(
        content for _, _, content in retrieved_context
    )

    return (
        "Based on the retrieved knowledge:\n"
        f"{context_text}"
    )


def process_user_query(query: str) -> str:
    """
    Route the query to a tool or the RAG knowledge base.
    """
    selected_tool = detect_tool(query)

    if selected_tool != "none":
        print(f"Route: Tool Calling ({selected_tool})")

        if selected_tool == "calculator":
            tool_input = extract_expression(query)
        else:
            tool_input = query

        return TOOLS[selected_tool](tool_input)

    print("Route: RAG Retrieval")

    retrieved_context = retrieve_context(query)
    return answer_from_context(query, retrieved_context)


# ---------------------------------------------------------
# 5. DEMONSTRATION
# ---------------------------------------------------------

def run_demo() -> None:
    sample_queries = [
        "What is Retrieval-Augmented Generation?",
        "Why are embeddings important in RAG?",
        "What is tool calling?",
        "Calculate 120 / 5 + 8",
        "What is today's date?",
        "Who is the president of France?",
    ]

    print("RAG AND TOOL CALLING ASSISTANT")
    print("=" * 65)

    for query in sample_queries:
        print("\n" + "=" * 65)
        print("User:", query)

        response = process_user_query(query)

        print("Assistant:")
        print(response)


if __name__ == "__main__":
    run_demo()
