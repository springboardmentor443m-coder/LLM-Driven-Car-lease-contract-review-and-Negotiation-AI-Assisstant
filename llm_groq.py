import requests
import os
from dotenv import load_dotenv
import os

load_dotenv()  # loads .env file

# Read key from environment (safer than hardcoding)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"


def call_groq(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert in car lease contracts, finance, and negotiation. "
                    "Explain contracts clearly and professionally."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)

    if response.status_code != 200:
        return f"Groq error: {response.text}"

    return response.json()["choices"][0]["message"]["content"]
