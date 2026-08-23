import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from config import LLM_MODEL

load_dotenv()


def load_llm():

    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0
    )

    return llm