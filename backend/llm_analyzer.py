import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# ✅ Create Gemini client (NO api_version)
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# -------------------------------
# RULE-BASED ANALYSIS (KEEP)
# -------------------------------
def analyze_contract(contract_text: str):
    risks = []
    text = contract_text.lower()

    if "months" in text and any(x in text for x in ["36", "48", "60"]):
        risks.append({
            "risk": "Long loan duration detected",
            "explanation": "Long duration increases total interest paid.",
            "negotiation_tip": "Request shorter tenure or lower interest."
        })

    if "penalty" in text or "late fee" in text:
        risks.append({
            "risk": "Penalty clause detected",
            "explanation": "Penalties can significantly increase cost.",
            "negotiation_tip": "Ask for a grace period."
        })

    if not risks:
        risks.append({
            "risk": "No major risks detected",
            "explanation": "Contract appears standard.",
            "negotiation_tip": "Negotiate minor benefits."
        })

    return risks


# -------------------------------
# ✅ REAL GEMINI AI ANALYSIS
# -------------------------------
def analyze_with_llm(contract_text: str):

    prompt = f"""
You are an AI legal assistant.

Analyze the following car lease or loan contract and provide:
1. Short summary
2. Risky clauses
3. Financial concerns
4. Negotiation advice
5. Overall risk level (Low / Medium / High)

Contract:
{contract_text}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        return response.text

    except Exception as e:
        return f"⚠️ AI service error: {e}"
