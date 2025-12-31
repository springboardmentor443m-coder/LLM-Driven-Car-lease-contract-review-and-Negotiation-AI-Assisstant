from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env from project root

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("GROQ_API_KEY not found")

client = Groq(api_key=api_key)

def generate_summary(text: str) -> str:
    prompt = f"""
    You are an auto lease expert.
    Summarize this car lease contract in simple English.
    Mention:
    - Monthly payment
    - APR
    - Any risks
    - Negotiation advice

    Contract text:
    {text}
    """

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # ✅ supported model
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return res.choices[0].message.content
