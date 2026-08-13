from langchain_google_genai import ChatGoogleGenerativeAI
from config import *

llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GOOGLE_API_KEY,
    temperature=0,
)