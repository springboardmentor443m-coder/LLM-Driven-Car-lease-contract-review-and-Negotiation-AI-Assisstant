import requests
import json

# 🔑 Paste your Groq API key here
GROQ_API_KEY = "ENTER YOUR API KEY"

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def generate_llm_explanation_groq(contract_json: dict) -> str:
    """
    Sends extracted contract data to Groq LLM
    and returns a natural language explanation.
    """

    prompt = f"""
You are an AI assistant that explains car lease contracts in simple language.

Explain the following contract by covering:
1. Key terms
2. Risks involved
3. Negotiation advice

Contract Data:
{json.dumps(contract_json, indent=2)}

Explain clearly for a normal user.
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You explain legal contracts clearly."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4
    }

    response = requests.post(GROQ_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise RuntimeError(f"Groq API error: {response.text}")

    return response.json()["choices"][0]["message"]["content"]

