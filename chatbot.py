import json
import requests

GROQ_API_KEY = "ENTER YOUR API KEY HERE"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.3-70b-versatile"  # use exact available model

def detect_intent(user_question):
    q = user_question.lower()

    if any(word in q for word in ["risk", "danger", "problem", "penalty", "unsafe"]):
        return "risk"
    elif any(word in q for word in ["negotiate", "reduce", "lower", "bargain"]):
        return "negotiation"
    elif any(word in q for word in ["explain", "summary", "overview"]):
        return "summary"
    elif any(word in q for word in ["mileage", "payment", "interest", "fee", "termination"]):
        return "clause"
    else:
        return "general"


def contract_chatbot(user_question, contract_data, chat_history):
    intent = detect_intent(user_question)

    intent_instruction = {
        "risk": "Focus on risks and explain why they are risky.",
        "negotiation": "Focus on what the user can negotiate and how.",
        "summary": "Give a simple overall explanation of the contract.",
        "clause": "Explain the specific clause clearly.",
        "general": "Answer clearly based on the contract data."
    }

    prompt = f"""
You are a car lease contract assistant chatbot.

Rules:
- Answer ONLY using the contract data.
- If information is missing, say "This information is not mentioned in the contract."
- Explain in simple language.

Conversation History:
{chat_history}

Contract Data:
{json.dumps(contract_data, indent=2)}

User Question:
{user_question}

Special Instruction:
{intent_instruction[intent]}

Answer:
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You explain car lease contracts clearly and honestly."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    response = requests.post(GROQ_URL, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]
