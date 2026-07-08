from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from tavily import TavilyClient
from config import (
    DB_FOLDER,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    GOOGLE_API_KEY,
    GEMINI_MODEL,
    TAVILY_API_KEY,
)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
DEBUG = False

# ---------------- Embeddings ---------------- #

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)

# ---------------- Vector DB ---------------- #

vector_db = Chroma(
    persist_directory=str(DB_FOLDER),
    embedding_function=embeddings,
    collection_name=COLLECTION_NAME,
)

print("Vector Count:", vector_db._collection.count())

# ---------------- Retriever ---------------- #

retriever = vector_db.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 20,
    },
)

# ---------------- LLM ---------------- #

llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GOOGLE_API_KEY,
    temperature=0,
)

chat_history = []

# ---------------- Prompt ---------------- #

prompt = ChatPromptTemplate.from_template(
"""
You are an intelligent RAG assistant.

Use ONLY the information present in the context.

If the context contains enough information, answer naturally.

Do not use your own knowledge.

Only reply:

"I don't know based on the provided documents."

when the answer is completely missing from the context.

Chat History:
{chat_history}

Context:
{context}

Question:
{question}

Answer:
"""
)

# ---------------- Chat History ---------------- #

def format_chat_history():
    history = ""

    for msg in chat_history[-6:]:
        if isinstance(msg, HumanMessage):
            history += f"User: {msg.content}\n"

        elif isinstance(msg, AIMessage):
            history += f"Assistant: {msg.content}\n"

    return history

# ---------------- Follow-up Detection ---------------- #

def is_followup_question(question):
    followup_words = [
        "it",
        "its",
        "this",
        "that",
        "they",
        "them",
        "he",
        "she",
        "his",
        "her",
        "those",
        "these",
    ]

    words = (
        question.lower()
        .replace("?", "")
        .replace(".", "")
        .split()
    )

    return any(word in words for word in followup_words)

# ---------------- Translation Tool ---------------- #

def translate_text(question):
    translation_prompt = f"""
You are a translation assistant.

Translate the user's text into the requested language.

If the user does not mention a language, translate into English.

Keep the meaning natural and simple.

User request:
{question}

Translation:
"""

    response = llm.invoke(translation_prompt)

    return response.content.strip()


def needs_translation(question):
    q = question.lower()

    translation_words = [
        "translate",
        "translation",
        "in english",
        "in urdu",
        "in hindi",
        "roman urdu",
        "urdu ma",
        "english ma",
        "is ko english",
        "is ko urdu",
    ]

    return any(word in q for word in translation_words)


def web_search(query, max_results=3):
    try:
        response = tavily_client.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
            include_answer=False,
            include_raw_content=False,
            include_images=False,
        )

        results = []

        for r in response.get("results", []):
            results.append(
                f"Title: {r.get('title')}\n"
                f"Link: {r.get('url')}\n"
                f"Content: {r.get('content')}"
            )

        if not results:
            return "No web results found."

        return "\n\n---------------------------\n\n".join(results)

    except Exception as e:
        return f"Web search failed: {e}"


web_prompt = ChatPromptTemplate.from_template(
"""
You are an intelligent assistant.

Use the web search results below to answer the question.

If the search results do not contain enough information, say:
"I don't know based on the web search results."

Web Search Results:
{context}

Question:
{question}

Answer:
"""
)
# ---------------- Ask Question ---------------- #

def ask_question(question):
    history = format_chat_history()

    # -------- Translation Tool -------- #

    if needs_translation(question):
        answer = translate_text(question)

        chat_history.append(HumanMessage(content=question))
        chat_history.append(AIMessage(content=answer))

        return answer

    # -------- RAG Document Search First -------- #

    if is_followup_question(question):
        search_query = f"""
Conversation:

{history}

Current Question:

{question}
"""
    else:
        search_query = question

    docs_with_scores = vector_db.similarity_search_with_score(
        search_query,
        k=8
    )

    RELEVANCE_THRESHOLD = 1.8

    docs = []

    for doc, score in docs_with_scores:
        if score <= RELEVANCE_THRESHOLD:
            docs.append(doc)

    if DEBUG:
        print("\nRetrieved Docs:", len(docs))

        for i, doc in enumerate(docs, start=1):
            print("\n" + "=" * 60)
            print("Document", i)
            print("=" * 60)

            print("Metadata:")
            print(doc.metadata)

            print("\nContent:\n")
            print(doc.page_content)

    # -------- If No Relevant Docs, Use Web Search -------- #

    if not docs:
        print("\nTool Called: Web Search")

        context = web_search(question)

        chain = web_prompt | llm

        response = chain.invoke(
            {
                "context": context,
                "question": question,
            }
        )

        answer = response.content.strip()

        chat_history.append(HumanMessage(content=question))
        chat_history.append(AIMessage(content=answer))

        return answer

    # -------- Answer From RAG Docs -------- #

    context = "\n\n---------------------------\n\n".join(
        doc.page_content for doc in docs
    )

    chain = prompt | llm

    response = chain.invoke(
        {
            "chat_history": history,
            "context": context,
            "question": question,
        }
    )

    answer = response.content.strip()

    # -------- If RAG Says Unknown, Use Web Search -------- #

    if "I don't know based on the provided documents." in answer:
        print("\nTool Called: Web Search")

        context = web_search(question)

        chain = web_prompt | llm

        response = chain.invoke(
            {
                "context": context,
                "question": question,
            }
        )

        answer = response.content.strip()

    chat_history.append(HumanMessage(content=question))
    chat_history.append(AIMessage(content=answer))

    return answer