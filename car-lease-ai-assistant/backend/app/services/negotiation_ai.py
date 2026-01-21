from app.services.groq_client import groq_chat

SYSTEM_PROMPT = """
You are an expert car lease negotiation assistant.
Give clear, actionable, and practical advice.
Use bullet points when helpful.
"""

def generate_negotiation_advice(ocr_text: str, question: str) -> str:
    prompt = f"""
Lease Contract Text:
{ocr_text}

User Question:
{question}
"""

    response = groq_chat(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=prompt
    )

    return response
