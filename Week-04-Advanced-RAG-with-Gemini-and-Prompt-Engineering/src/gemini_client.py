"""
Gemini Test
"""

from src.gemini_client import GeminiClient

client = GeminiClient()

print(client.health_check())

print(

    client.generate_response(

        "Explain Artificial Intelligence."

    )

)