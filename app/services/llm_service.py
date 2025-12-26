from groq import Groq
from langchain_groq import ChatGroq

def base_llm(api_key):
    return Groq(api_key=api_key)

def chat_llm(api_key):
    return ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0
    )
