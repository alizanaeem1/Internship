"""
Utility Functions
"""

import logging

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s"

)


logger = logging.getLogger(__name__)


def clean_text(text):

    return text.replace("\n", " ").strip()


def estimate_tokens(text):

    return len(text.split())


def print_divider():

    print("=" * 80)


def log_query(query):

    logger.info(f"User Query : {query}")


def log_response():

    logger.info("Response Generated Successfully")


def chunk_text(text, size=500):

    words = text.split()

    chunks = []

    for i in range(0, len(words), size):

        chunks.append(

            " ".join(words[i:i + size])

        )

    return chunks