# negotiator.py
"""
Generate negotiation messages based on contract analysis
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


def generate_negotiation_messages(structured_data: dict, fairness_score: int, score_reasons: list) -> dict:
    """
    Generate three types of negotiation messages:
    1. Polite - Friendly approach
    2. Firm - Direct but professional
    3. Legal-based - Citing specific concerns
    
    Returns dict with: polite, firm, legal_based
    """
    
    core = structured_data.get("core", {})
    financial = structured_data.get("financial_analysis", {})
    
    # Extract key details
    vehicle = f"{core.get('year', '')} {core.get('make', '')} {core.get('model', '')}".strip()
    monthly = core.get("monthly_payment", "N/A")
    apr = core.get("apr", "N/A")
    term = core.get("term_months", "N/A")
    price = financial.get("vehicle_price", "N/A")
    
    # Build context for AI
    context = f"""
Vehicle: {vehicle}
Price: {price}
Monthly Payment: {monthly}
Term: {term} months
APR: {apr}
Fairness Score: {fairness_score}/100

Issues identified:
{chr(10).join('- ' + reason for reason in score_reasons)}
"""
    
    if not groq_client:
        # Fallback templates if LLM not available
        return _generate_template_messages(vehicle, monthly, apr, fairness_score, score_reasons)
    
    try:
        # Generate all three message styles in one call
        prompt = f"""
You are a car buying negotiation expert. Based on this contract analysis, generate THREE negotiation messages:

{context}

Generate three distinct messages:

1. POLITE: Friendly, collaborative tone
2. FIRM: Direct, professional, assertive
3. LEGAL_BASED: Reference specific contract terms and legal standards

Return ONLY this JSON format:
{{
  "polite": "message text here",
  "firm": "message text here",
  "legal_based": "message text here"
}}

Each message should:
- Be 3-5 sentences
- Reference specific concerns from the analysis
- Request specific improvements
- Be ready to send to a dealer

Return ONLY valid JSON.
"""
        
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.7,
            messages=[
                {"role": "system", "content": "You are a negotiation expert. Return only JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        
        result_text = response.choices[0].message.content
        
        # Parse JSON
        import json
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]
        
        messages = json.loads(result_text.strip())
        
        # Validate all three message types exist
        for msg_type in ["polite", "firm", "legal_based"]:
            if msg_type not in messages or not messages[msg_type]:
                messages[msg_type] = f"Unable to generate {msg_type} message. Please review contract manually."
        
        return messages
    
    except Exception as e:
        print(f"[NEGOTIATOR ERROR] {str(e)}")
        return _generate_template_messages(vehicle, monthly, apr, fairness_score, score_reasons)


def _generate_template_messages(vehicle: str, monthly: str, apr: str, fairness_score: int, reasons: list) -> dict:
    """
    Fallback template messages when LLM is unavailable
    """
    
    # Identify top 2 concerns
    top_concerns = reasons[1:3] if len(reasons) > 2 else reasons
    concerns_text = " Additionally, ".join(top_concerns) if top_concerns else "several concerns with the terms"
    
    polite = f"""
Hi, I'm very interested in the {vehicle}, but after reviewing the contract details, I noticed {concerns_text}. 
I'd love to work together to find terms that work better for both of us. Would you be open to discussing 
the {monthly} monthly payment and {apr} APR? I'm a serious buyer and would like to move forward if we can 
reach an agreement. Thank you for your time!
"""
    
    firm = f"""
I've reviewed the contract for the {vehicle} and have concerns about several terms. The current fairness 
score based on market standards is {fairness_score}/100. Specifically: {concerns_text}. I need you to 
revise the {monthly} monthly payment and {apr} APR to market-competitive rates before I can proceed. 
Please provide an updated offer within 48 hours.
"""
    
    legal_based = f"""
After thorough analysis of the proposed contract for the {vehicle}, I must highlight several terms that 
don't align with industry standards and consumer protection guidelines. {concerns_text}. Per Truth in 
Lending Act requirements, I'm requesting full disclosure of all fees and a revised offer with competitive 
rates. The current {apr} APR and {monthly} monthly payment structure require adjustment to reflect fair 
market terms. Please provide documentation supporting these charges or submit revised terms.
"""
    
    return {
        "polite": polite.strip(),
        "firm": firm.strip(),
        "legal_based": legal_based.strip()
    }