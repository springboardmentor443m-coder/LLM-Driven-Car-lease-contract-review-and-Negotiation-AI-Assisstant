import json
import requests
import os
from typing import Optional, List, Dict


# ======================================================
# GROQ CONFIG
# ======================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Use a currently supported production model
MODEL_NAME = "openai/gpt-oss-20b"


# ======================================================
# INTENT DETECTION
# ======================================================

def detect_intent(question: str) -> str:

    q = question.lower()

    if any(w in q for w in [
        "risk",
        "risky",
        "danger",
        "problem",
        "penalty",
        "bad"
    ]):
        return "risk"

    if any(w in q for w in [
        "negotiate",
        "negotiation",
        "reduce",
        "lower",
        "bargain",
        "discount"
    ]):
        return "negotiation"

    if any(w in q for w in [
        "summary",
        "overview",
        "summarize",
        "explain contract"
    ]):
        return "summary"

    if any(w in q for w in [
        "mileage",
        "payment",
        "interest",
        "apr",
        "termination",
        "penalty"
    ]):
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

    # ==================================================
    # CHECK API KEY
    # ==================================================

    if not GROQ_API_KEY:

        return (
            "LLM API key is not configured. "
            "Please configure GROQ_API_KEY and restart the backend."
        )


    # ==================================================
    # DETECT INTENT
    # ==================================================

    intent = detect_intent(question)


    intent_instruction = {

        "risk":
            "Explain the risks in the contract and why they matter to the user.",

        "negotiation":
            "Identify terms that may potentially be negotiated and suggest reasonable questions the user can ask.",

        "summary":
            "Give a simple and easy-to-understand summary of the contract.",

        "clause":
            "Explain the requested contract clause clearly using only the available contract information.",

        "general":
            "Answer the user's question clearly using the contract information."
    }


    # ==================================================
    # CONVERSATION HISTORY
    # ==================================================

    history_text = "\n".join(chat_history[-6:]) if chat_history else "No previous conversation."


    # ==================================================
    # PROMPT
    # ==================================================

    prompt = f"""
You are an AI assistant that helps users understand car loan and lease contracts.

Your job is to answer questions about the uploaded contract.

IMPORTANT RULES:

1. Use ONLY the information provided below.
2. Do NOT invent contract information.
3. Do NOT assume missing values.
4. If information is unavailable, clearly say:
   "This information is not available in the contract."
5. Keep answers simple and easy to understand.
6. If the user asks about the vehicle, use Vehicle Information when available.
7. If the user asks about the contract, prioritize Contract Text and SLA Data.
8. You may explain the meaning of terms such as APR, mileage limit, penalties, etc.
9. For negotiation questions, suggest questions the user could ask the lender/dealer.
10. Do not present assumptions as facts.

--------------------------------------------------
CONVERSATION HISTORY
--------------------------------------------------

{history_text}

--------------------------------------------------
CONTRACT TEXT
--------------------------------------------------

{contract_text[:5000]}

--------------------------------------------------
SLA DATA
--------------------------------------------------

{json.dumps(sla, indent=2)}

--------------------------------------------------
VEHICLE INFORMATION
--------------------------------------------------

{json.dumps(vehicle_info, indent=2) if vehicle_info else "Not available"}

--------------------------------------------------
USER QUESTION
--------------------------------------------------

{question}

--------------------------------------------------
INSTRUCTION
--------------------------------------------------

{intent_instruction[intent]}
"""


    # ==================================================
    # REQUEST HEADERS
    # ==================================================

    headers = {

        "Authorization": f"Bearer {GROQ_API_KEY}",

        "Content-Type": "application/json"
    }


    # ==================================================
    # REQUEST PAYLOAD
    # ==================================================

    payload = {

        "model": MODEL_NAME,

        "messages": [

            {
                "role": "system",
                "content":
                    "You are a helpful AI assistant specialized in car contracts."
            },

            {
                "role": "user",
                "content": prompt
            }
        ],

        "temperature": 0.2,

        "max_tokens": 1000
    }


    # ==================================================
    # CALL GROQ
    # ==================================================

    try:

        response = requests.post(

            GROQ_URL,

            headers=headers,

            json=payload,

            timeout=30
        )


        # ==================================================
        # HANDLE API ERRORS
        # ==================================================

        # if response.status_code != 200:

        #     print(
        #         "❌ Groq API Error:",
        #         response.status_code,
        #         response.text
        #     )

        #     return (
        #         "The AI service could not process the request. "
        #         "Please try again."
        #     )

        if response.status_code != 200:
            print("====================================")
            print("❌ GROQ API ERROR")
            print("STATUS:", response.status_code)
            print("RESPONSE:", response.text)
            print("====================================")

            return f"Groq API Error {response.status_code}: {response.text}"


        # ==================================================
        # PARSE RESPONSE
        # ==================================================

        data = response.json()


        choices = data.get("choices", [])

        if not choices:

            return "The AI service returned an empty response."


        message = choices[0].get("message", {})

        answer = message.get("content")


        if not answer:

            return "The AI service did not generate an answer."


        return answer.strip()


    # ==================================================
    # NETWORK ERROR
    # ==================================================

    except requests.exceptions.Timeout:

        print("❌ Groq request timed out.")

        return (
            "The AI service is taking too long to respond. "
            "Please try again."
        )


    except requests.exceptions.RequestException as e:

        print("❌ Groq request failed:", e)

        return (
            "Network error while contacting the AI service."
        )


    # ==================================================
    # UNEXPECTED ERROR
    # ==================================================

    except Exception as e:

        print("❌ Unexpected chatbot error:", e)

        return (
            "Unexpected error occurred while processing your question."
        )