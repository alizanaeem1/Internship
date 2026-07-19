"""
Week 2 - Tool Calling Demonstration

This program demonstrates:

1. Defining tools
2. Registering tools
3. Detecting user intent
4. Selecting the correct tool
5. Executing the tool
6. Returning the result

The example uses local tools so that it can run without an API.
"""

from datetime import datetime
from typing import Any, Callable, Dict
import ast
import operator
import re


# ---------------------------------------------------------
# 1. SAFE CALCULATOR
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


def evaluate_expression(node: ast.AST) -> float:
    """Safely evaluate a mathematical expression."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
        left_value = evaluate_expression(node.left)
        right_value = evaluate_expression(node.right)
        return ALLOWED_OPERATORS[type(node.op)](
            left_value,
            right_value,
        )

    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPERATORS:
        return ALLOWED_OPERATORS[type(node.op)](
            evaluate_expression(node.operand)
        )

    raise ValueError("Unsupported mathematical expression.")


def calculator_tool(expression: str) -> str:
    """Calculate a mathematical expression safely."""
    try:
        parsed_expression = ast.parse(expression, mode="eval")
        result = evaluate_expression(parsed_expression.body)
        return f"Calculation result: {result}"
    except (SyntaxError, ValueError, ZeroDivisionError) as error:
        return f"Calculation error: {error}"


# ---------------------------------------------------------
# 2. DATE AND TIME TOOL
# ---------------------------------------------------------

def current_date_tool(_: str = "") -> str:
    """Return the current local date and time."""
    now = datetime.now()
    return now.strftime(
        "Current date and time: %A, %d %B %Y, %I:%M %p"
    )


# ---------------------------------------------------------
# 3. LOCAL SEARCH TOOL
# ---------------------------------------------------------

SEARCH_DATA = {
    "rag": (
        "RAG combines document retrieval with language-model generation."
    ),
    "embedding": (
        "An embedding is a numerical representation of text or other data."
    ),
    "vector database": (
        "A vector database stores embeddings and performs similarity search."
    ),
    "tool calling": (
        "Tool calling allows an AI system to select and execute a function."
    ),
}


def local_search_tool(query: str) -> str:
    """Search a small local dictionary."""
    normalized_query = query.lower()

    for topic, information in SEARCH_DATA.items():
        if topic in normalized_query:
            return f"Search result: {information}"

    return "No matching search result was found."


# ---------------------------------------------------------
# 4. TOOL REGISTRY
# ---------------------------------------------------------

ToolFunction = Callable[[str], str]

TOOLS: Dict[str, Dict[str, Any]] = {
    "calculator": {
        "description": "Performs arithmetic calculations.",
        "function": calculator_tool,
    },
    "current_date": {
        "description": "Returns the current date and time.",
        "function": current_date_tool,
    },
    "local_search": {
        "description": "Searches local technical information.",
        "function": local_search_tool,
    },
}


# ---------------------------------------------------------
# 5. INTENT DETECTION
# ---------------------------------------------------------

def extract_math_expression(query: str) -> str:
    """Extract a mathematical expression from a query."""
    matches = re.findall(r"[0-9+\-*/().%\s]+", query)

    if not matches:
        return ""

    return max(matches, key=len).strip()


def select_tool(query: str) -> str:
    """Select the most suitable tool based on the query."""
    normalized_query = query.lower()

    date_keywords = [
        "date",
        "time",
        "today",
        "current day",
    ]

    search_keywords = [
        "search",
        "find",
        "what is rag",
        "embedding",
        "vector database",
        "tool calling",
    ]

    if any(keyword in normalized_query for keyword in date_keywords):
        return "current_date"

    expression = extract_math_expression(query)
    if expression and any(symbol in expression for symbol in "+-*/%"):
        return "calculator"

    if any(keyword in normalized_query for keyword in search_keywords):
        return "local_search"

    return "none"


def prepare_tool_input(tool_name: str, query: str) -> str:
    """Prepare the input required by the selected tool."""
    if tool_name == "calculator":
        return extract_math_expression(query)

    if tool_name in {"local_search", "current_date"}:
        return query

    return ""


def call_tool(tool_name: str, tool_input: str) -> str:
    """Execute a registered tool."""
    tool = TOOLS.get(tool_name)

    if tool is None:
        return "Requested tool is not available."

    function: ToolFunction = tool["function"]
    return function(tool_input)


def process_query(query: str) -> str:
    """Select a tool, call it, and return the result."""
    selected_tool = select_tool(query)

    print(f"Selected Tool: {selected_tool}")

    if selected_tool == "none":
        return (
            "No suitable tool was identified for this query."
        )

    tool_input = prepare_tool_input(selected_tool, query)
    print(f"Tool Input: {tool_input}")

    return call_tool(selected_tool, tool_input)


def display_tools() -> None:
    """Display all registered tools."""
    print("AVAILABLE TOOLS")
    print("=" * 60)

    for tool_name, tool_details in TOOLS.items():
        print(f"{tool_name}: {tool_details['description']}")


def run_demo() -> None:
    """Run sample tool-calling queries."""
    display_tools()

    sample_queries = [
        "Calculate 25 * 4 + 10",
        "What is the current date and time?",
        "Search what is RAG",
        "Explain software testing",
    ]

    for query in sample_queries:
        print("\n" + "=" * 60)
        print("User Query:", query)
        result = process_query(query)
        print("Tool Result:", result)


if __name__ == "__main__":
    run_demo()
