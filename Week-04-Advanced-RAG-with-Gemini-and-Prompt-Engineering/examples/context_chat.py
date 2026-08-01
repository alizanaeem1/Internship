"""
Context Aware Chat
"""

from src.answer_generator import AnswerGenerator

chatbot = AnswerGenerator()

print("=" * 80)
print("Context Aware AI Assistant")
print("=" * 80)

while True:

    question = input("\nQuestion : ")

    if question.lower() == "exit":
        break

    answer = chatbot.generate(question)

    print("\nAnswer:\n")

    print(answer)