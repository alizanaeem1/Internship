"""
Context Manager
"""

class ContextManager:

    def __init__(self):

        self.max_length = 4000

    def remove_duplicates(self, docs):

        unique = []

        seen = set()

        for doc in docs:

            if doc.page_content not in seen:

                seen.add(doc.page_content)

                unique.append(doc)

        return unique

    def trim_context(self, context):

        if len(context) <= self.max_length:

            return context

        return context[: self.max_length]

    def prepare_context(self, docs):

        docs = self.remove_duplicates(docs)

        context = ""

        for doc in docs:

            context += doc.page_content

            context += "\n\n"

        return self.trim_context(context)