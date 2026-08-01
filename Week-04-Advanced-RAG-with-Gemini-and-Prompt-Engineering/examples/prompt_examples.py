"""
Prompt Engineering Examples
"""

from src.prompt_engineering import (
    build_prompt,
    summarize_prompt,
    translate_prompt
)

context = """
RAG combines retrieval with LLMs.
"""

question = "Explain RAG."

print(build_prompt(context, question))

print("=" * 80)

print(

    summarize_prompt(context)

)

print("=" * 80)

print(

    translate_prompt("یہ اردو زبان ہے۔")

)