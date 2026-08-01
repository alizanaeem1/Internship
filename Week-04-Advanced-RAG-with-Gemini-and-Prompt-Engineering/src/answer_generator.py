"""
Answer Generator
"""

from src.prompt_engineering import build_prompt
from src.gemini_client import GeminiClient
from src.rag_pipeline import RAGPipeline


class AnswerGenerator:

    def __init__(self):

        self.rag = RAGPipeline()

        self.gemini = GeminiClient()

    def generate(self, question):

        documents = self.rag.retrieve_documents(question)

        context = self.rag.build_context(documents)

        prompt = build_prompt(context, question)

        answer = self.gemini.generate_response(prompt)

        return answer