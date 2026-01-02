import json
import requests
import os
from typing import Optional, List, Dict


# ======================================================
# GROQ CONFIG
# ======================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.3-70b-versatile"


# ======================================================
# INTENT DETECTION
# ======================================================
def detect_intent(question: str) -> str:
    q = question.lower()

    if any(w in q for w in ["risk", "danger", "problem", "penalty"]):
        return "risk"
    if any(w in q for w in ["negotiate", "reduce", "lower", "bargain"]):
        return "negotiation"
    if any(w in q for w in ["summary", "overview", "explain"]):
        return "summary"
    if any(w in q for w in ["mileage", "payment", "interest", "termination"]):
        return "clause"

    return "general"


# ======================================================
# MAIN CHAT FUNCTION
# ======================================================
def generate_chat_response(
    question: str,
    contract_text: str,
    sla: Dict,
    vehicle_info: Optional[Dict],
    chat_history: List[str]
) -> str:

    # 🔒 HARD FAIL IF API KEY MISSING
    if not GROQ_API_KEY:
        return "LLM API key is not configured. Please contact administrator."

    intent = detect_intent(question)

    intent_instruction = {
        "risk": "Explain risks and why they matter.",
        "negotiation": "Suggest what can be negotiated.",
        "summary": "Give a simple overall explanation.",
        "clause": "Explain the clause clearly.",
        "general": "Answer clearly using the contract."
    }

    prompt = f"""
You are an AI assistant that helps users understand car loan/lease contracts.

Rules:
- Use ONLY the given data
- Do NOT hallucinate
- If something is missing, say so clearly
- Be simple, honest, and professional

Conversation History:
{"\n".join(chat_history[-6:])}

Contract Text:
{contract_text[:3000]}

SLA Data:
{json.dumps(sla, indent=2)}

Vehicle Info:
{json.dumps(vehicle_info, indent=2) if vehicle_info else "Not available"}

User Question:
{question}

Instruction:
{intent_instruction[intent]}
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You explain car contracts clearly."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post(
            GROQ_URL,
            headers=headers,
            json=payload,
            timeout=20
        )

        # ❌ DO NOT CRASH FASTAPI
        if response.status_code != 200:
            print("❌ Groq API Error:", response.text)
            return "AI service is temporarily unavailable. Please try again later."

        data = response.json()

        # Defensive parsing
        return (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "No response generated.")
        )

    except requests.exceptions.RequestException as e:
        print("❌ Request failed:", e)
        return "Network error while contacting AI service."

    except Exception as e:
        print("❌ Unexpected chatbot error:", e)
        return "Unexpected error occurred while processing your request."
