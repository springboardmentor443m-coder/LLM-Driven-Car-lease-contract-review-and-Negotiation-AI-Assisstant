import json
import re
from groq import Groq

# Initialize Groq client
client = Groq()

# Expected SLA schema (keys must always exist)
SLA_SCHEMA = {
    "apr": None,
    "lease_term_months": None,
    "monthly_payment": None,
    "down_payment": None,
    "residual_value": None,
    "mileage_limit": None,
    "overage_fee": None,
    "early_termination_clause": None,
    "buyout_price": None,
    "maintenance_responsibility": None,
    "warranty_insurance": None,
    "penalties": None,
    "red_flags": []
}


def _extract_json_safely(llm_output: str) -> dict:
    """
    Extract the first valid JSON object from LLM output.
    Handles extra text, markdown, explanations, etc.
    """
    match = re.search(r"\{.*\}", llm_output, re.DOTALL)

    if not match:
        raise ValueError("No JSON object found in LLM output")

    json_str = match.group(0)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON extracted: {str(e)}")


def extract_sla(ocr_text: str) -> dict:
    """
    Extract SLA fields from OCR text using Groq LLM.
    Returns validated structured JSON.
    """

    prompt = f"""
You are an information extraction engine.

TASK:
Extract SLA fields from the following car lease or loan contract.

STRICT RULES:
- Output MUST be valid JSON
- Output MUST start with {{ and end with }}
- Do NOT include explanations, markdown, or comments
- Use null for missing fields
- Numeric fields must be numbers only (no symbols like $ or %)
- red_flags must be an array of strings

FIELDS:
{json.dumps(list(SLA_SCHEMA.keys()), indent=2)}

CONTRACT TEXT:
\"\"\"
{ocr_text}
\"\"\"
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # stable text-only model
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    raw_output = response.choices[0].message.content.strip()

    # DEBUG (optional – comment out later)
    # print("RAW LLM OUTPUT:\n", raw_output)

    # Extract JSON safely
    data = _extract_json_safely(raw_output)

    # Ensure all keys exist
    for key in SLA_SCHEMA:
        if key not in data:
            data[key] = None

    # Ensure red_flags is always a list
    if not isinstance(data.get("red_flags"), list):
        data["red_flags"] = []

    return data
