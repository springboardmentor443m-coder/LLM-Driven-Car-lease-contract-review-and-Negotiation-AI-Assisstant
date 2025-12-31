from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def chatbot_response(question, data):
    prompt = f"""
    You are a car lease assistant.

    Lease data:
    {data}

    Question:
    {question}
    """

    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return res.choices[0].message.content

    except Exception:
        return "Sorry, I couldn't answer that right now."
