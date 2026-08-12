import os

from dotenv import load_dotenv

from langchain_groq import ChatGroq

from config import LLM_MODEL

load_dotenv()


def load_llm():

    llm = ChatGroq(
        model=LLM_MODEL,
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0
    )

    return llm