"""
Prompt Templates
"""

SYSTEM_PROMPT = """
You are an intelligent AI assistant.

Rules:

1. Answer ONLY from context.

2. Never hallucinate.

3. If answer not found,

reply politely.

4. Keep response concise.

5. Use bullet points whenever possible.
"""


def build_prompt(context, question):

    return f"""

{SYSTEM_PROMPT}

Context:

{context}

Question:

{question}

Generate an accurate answer.

"""


def summarize_prompt(text):

    return f"""

Summarize the following text.

{text}

"""


def translate_prompt(text):

    return f"""

Translate into English.

{text}

"""