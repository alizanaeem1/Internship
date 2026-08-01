"""
Basic Gemini Chat Example
"""

from src.gemini_client import GeminiClient

gemini = GeminiClient()

print("=" * 80)
print("Gemini Chat")
print("=" * 80)

while True:

    question = input("\nYou : ")

    if question.lower() == "exit":
        break

    answer = gemini.generate_response(question)

    print("\nGemini :", answer)