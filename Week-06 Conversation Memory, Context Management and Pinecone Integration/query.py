from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from followup import is_related, rewrite_question
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from  followup import extract_topic
last_question = None
last_answer = None
current_topic = None
from config import (
   PINECONE_API_KEY,
   PINECONE_INDEX,
    EMBEDDING_MODEL,
    TOP_K,
    FETCH_K,
    DEBUG,
)


OUT_OF_CONTEXT_RESPONSE = (
    "Sorry, this information is not available in my QHSE and DOT Compliance knowledge base. "
    "Please ask a question related to QHSE or DOT Compliance."
)

# ---------------- Embeddings ---------------- #

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)


# ---------------- Vector DB ---------------- #

pc = Pinecone(api_key=PINECONE_API_KEY)

index = pc.Index(PINECONE_INDEX)

vector_db = PineconeVectorStore(
    index=index,
    embedding=embeddings,
)

print("=" * 50)
print("Connected to Pinecone")
print("=" * 50)


# ---------------- Retriever ---------------- #

retriever = vector_db.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": TOP_K,
        "fetch_k": FETCH_K,
    },
)

from config import GOOGLE_API_KEY, GEMINI_MODEL

print("=" * 50)
print("API KEY:", GOOGLE_API_KEY)
print("MODEL:", GEMINI_MODEL)
print("=" * 50)
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
You are a professional QHSE and DOT Compliance assistant.

You answer ONLY using the provided knowledge base.

The knowledge base contains:

QHSE
- Quality
- Health
- Safety
- Environment
- ISO 9001
- ISO 14001
- ISO 45001
- Risk Management
- Audits
- CAPA
- RCA
- HIRA
- JSA
- PPE
- PTW
- LOTO

DOT Compliance
- FMCSA
- PHMSA
- Commercial Drivers
- Driver Qualification
- Driver Qualification File (DQF)
- CDL
- Medical Certificate
- Vehicle Inspection
- DVIR
- Hours of Service (HOS)
- Electronic Logging Device (ELD)
- Drug & Alcohol Testing
- Hazardous Materials (HazMat)
- Shipping Papers
- Placards
- Cargo Securement
- Accident Reporting
- Fleet Maintenance

Rules:
1. Answer ONLY using the provided knowledge base.
2. Never use outside knowledge or guess.
3. Use all retrieved information to answer the question, even if the information is spread across multiple documents.
4. If the exact question is not explicitly answered but the retrieved information is sufficient, provide the best answer based only on the retrieved information.
5. If multiple retrieved documents contain relevant information, combine them into one complete and well-structured answer.
6. Keep the answer clear, professional, and concise.
7. Use bullet points when helpful.
8. Do not mention "context", "documents", or "retrieved information" in your response.
9. Return the following response ONLY when none of the retrieved documents contain information relevant to the user's question:
"{out_of_context_response}"
10. Adjust the level of detail based on the user's question.

11. If the user asks "What is...", "Define...", or requests only a definition, provide a concise answer (2–5 sentences) using only the relevant information.

12. If the user asks "Explain...", "Describe...", "How...", "Why...", "List...", "Compare...", or requests detailed or complete information, provide a comprehensive answer by combining all relevant retrieved information.

13. When providing a detailed answer, include relevant sections such as:
- Definition
- Importance
- Key Points
- Implementation Guidance
- Common Records
- Summary

Only include the sections that are relevant to the user's question.

14. Use headings and bullet points where appropriate.

Chat History:
{chat_history}

Knowledge Base Context:
{context}

User Question:
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


# def is_followup_question(question: str) -> bool:
#     q = question.lower().strip()

#     followup_phrases = [
#         "explain more",
#         "tell me more",
#         "more detail",
#         "example",
#         "another example",
#         "what about",
#         "why",
#         "how about",
#     ]

#     followup_words = {
#         "it",
#         "its",
#         "this",
#         "that",
#         "they",
#         "them",
#         "those",
#         "these",
#     }

#     words = set(
#         q.replace("?", "")
#          .replace(".", "")
#          .replace(",", "")
#          .split()
#     )

#     return (
#         any(p in q for p in followup_phrases)
#         or bool(words.intersection(followup_words))
#     )



# ---------------- QHSE Guard ---------------- #

# def is_likely_domain_question(question: str) -> bool:
#     """
#     Prevents obvious questions outside the QHSE and DOT Compliance scope.
#     """

#     domain_keywords = {
#         # QHSE
#         "qhse",
#         "hse",
#         "quality",
#         "health",
#         "safety",
#         "environment",
#         "environmental",
#         "iso",
#         "9001",
#         "14001",
#         "45001",
#         "qa",
#         "qc",
#         "quality assurance",
#         "quality control",
#         "process quality",
#         "product quality",
#         "inspection",
#         "testing",
#         "defect",
#         "defects",
#         "specification",
#         "specifications",
#         "risk",
#         "annex",
#         "annex sl",
#         "management system",
#         "integrated management system",
#         "ims",
#         "sop",
#         "sops",
#         "standard operating procedure",
#         "toolbox",
#         "toolbox talk",
#         "chemical",
#         "chemical exposure",
#         "exposure control",
#         "energy conservation",
#         "crisis",
#         "crisis management",
#         "business continuity",
#         "document approval",
#         "document control",
#         "life cycle",
#         "life-cycle",
#         "dashboard",
#         "kpi",
#         "kpis",
#         "hazard",
#         "incident",
#         "accident",
#         "near miss",
#         "ppe",
#         "ptw",
#         "permit to work",
#         "loto",
#         "lockout",
#         "tagout",
#         "fire",
#         "electrical",
#         "confined space",
#         "working at height",
#         "waste",
#         "spill",
#         "pollution",
#         "capa",
#         "corrective action",
#         "preventive action",
#         "rca",
#         "root cause",
#         "hira",
#         "jsa",
#         "fmea",
#         "audit",
#         "nonconformity",
#         "ncr",
#         "ergonomics",
#         "medical surveillance",
#         "industrial hygiene",
#         "heat stress",
#         "cold stress",
#         "noise",
#         "occupational",
#         "emergency",
#         "training",
#         "compliance",

#         # DOT
#         "dot",
#         "department of transportation",
#         "fmcsa",
#         "phmsa",
#         "commercial driver",
#         "commercial drivers",
#         "commercial motor vehicle",
#         "commercial vehicle",
#         "cmv",
#         "cdl",
#         "commercial driver license",
#         "driver qualification",
#         "driver qualification file",
#         "dqf",
#         "motor vehicle record",
#         "mvr",
#         "medical examiner certificate",
#         "medical card",
#         "driver monitoring",
#         "driver disqualification",
#         "driver performance",
#         "road test",
#         "vehicle inspection",
#         "vehicle maintenance",
#         "preventive maintenance",
#         "fleet maintenance",
#         "dvir",
#         "driver vehicle inspection report",
#         "pre-trip",
#         "pre trip",
#         "post-trip",
#         "post trip",
#         "annual vehicle inspection",
#         "roadside inspection",
#         "out of service",
#         "out-of-service",
#         "oos",
#         "brake inspection",
#         "tire inspection",
#         "steering inspection",
#         "suspension inspection",
#         "cargo securement",
#         "hours of service",
#         "hos",
#         "duty status",
#         "11-hour",
#         "11 hour",
#         "14-hour",
#         "14 hour",
#         "30-minute break",
#         "30 minute break",
#         "60/70-hour",
#         "60/70 hour",
#         "sleeper berth",
#         "electronic logging device",
#         "eld",
#         "driver log",
#         "drug testing",
#         "alcohol testing",
#         "random testing",
#         "reasonable suspicion",
#         "post-accident testing",
#         "return-to-duty",
#         "return to duty",
#         "follow-up testing",
#         "hazmat",
#         "hazardous material",
#         "hazardous materials",
#         "placard",
#         "placards",
#         "hazard label",
#         "shipping papers",
#         "accident reporting",
#         "incident investigation",
#         "accident recordkeeping",
#     }

#     question_lower = question.lower()
#     return any(keyword in question_lower for keyword in domain_keywords)
   
# ---------------- Helpers ---------------- #

def format_docs(docs):
    formatted = []

    for i, doc in enumerate(docs, start=1):
        title = doc.metadata.get("title", "Unknown Title")
        category = doc.metadata.get("category", "Unknown Category")
        file_name = doc.metadata.get("file_name", "unknown file")

        formatted.append(
            f"Source {i}\n"
            f"Title: {title}\n"
            f"Category: {category}\n"
            f"File: {file_name}\n\n"
            f"{doc.page_content}"
        )

    return "\n\n---------------------------\n\n".join(formatted)


def remove_duplicate_docs(docs):
    unique_docs = []
    seen = set()

    for doc in docs:
        text = " ".join(doc.page_content.split()).lower()

        if text in seen:
            continue

        seen.add(text)
        unique_docs.append(doc)

    return unique_docs


# ---------------- Ask Question ---------------- #
def ask_question(question: str) -> str:

    global last_question, last_answer, current_topic

    question = question.strip()

    if not question:
        return "Please enter a QHSE or DOT Compliance-related question."

    history = format_chat_history()

    search_query = question

    # -----------------------------
    # Follow-up Detection
    # -----------------------------
    if last_question is not None:

        related = is_related(
            previous_question=last_question,
            current_question=question,
            llm=llm,
        )

        

        if related:

            search_query = rewrite_question(
                previous_context=current_topic,
                current_question=question,
                llm=llm,
            )

           

        else:
            current_topic = extract_topic(question, llm)
            search_query = question

    else:
        current_topic = extract_topic(question, llm)
        search_query = question

        

   
   
    # -----------------------------
    # Retrieve Documents
    # -----------------------------
    results = vector_db.similarity_search_with_score(
    search_query,
    k=TOP_K,
    )

    

    

    if not results:
        return OUT_OF_CONTEXT_RESPONSE

    MIN_SCORE = 0.35

    docs = [doc for doc, score in results]

    docs = remove_duplicate_docs(docs)

    if not docs:
        return OUT_OF_CONTEXT_RESPONSE


    if DEBUG:
        for i, doc in enumerate(docs, start=1):
            print("\n" + "=" * 60)
            print(f"Document {i}")
            print("=" * 60)
            print(doc.metadata)
            print(doc.page_content[:500])

    # -----------------------------
    # Build Context
    # -----------------------------
    context = format_docs(docs)

    if DEBUG:
        print("=" * 100)
        print(context)
        print("=" * 100)

    chain = prompt | llm

    response = chain.invoke(
        {
            "chat_history": history,
            "context": context,
            "question": search_query,
            "out_of_context_response": OUT_OF_CONTEXT_RESPONSE,
        }
    )

    answer = response.content.strip()

    if not answer:
        answer = OUT_OF_CONTEXT_RESPONSE

    chat_history.append(HumanMessage(content=question))
    chat_history.append(AIMessage(content=answer))

    last_question = question
    last_answer = answer

    return answer