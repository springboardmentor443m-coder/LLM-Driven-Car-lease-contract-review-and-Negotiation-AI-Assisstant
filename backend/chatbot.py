from backend.gemini_client import get_gemini_client

# Create Gemini client
client = get_gemini_client()

def chatbot_response(user_question, contract_text=None, vehicle_data=None):
    """
    Gemini-powered AI chatbot for car lease assistance
    """

    context = ""

    if contract_text:
        context += f"""
Contract Extract:
{contract_text[:1500]}
"""

    if vehicle_data:
        context += f"""
Vehicle Details:
Make: {vehicle_data.get("Make")}
Model: {vehicle_data.get("Model")}
Year: {vehicle_data.get("ModelYear")}
Fuel Type: {vehicle_data.get("FuelTypePrimary")}
"""

    prompt = f"""
You are an intelligent AI assistant specialized in car lease and loan guidance.

Your tasks:
- Answer user questions clearly
- Explain contract risks
- Give negotiation advice
- Help with EMI and pricing doubts

Use the provided context if available.

Context:
{context}

User Question:
{user_question}

Give a clear, friendly, professional answer.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        return response.text

    except Exception:
        return "⚠️ AI service temporarily unavailable. Please try again later."
