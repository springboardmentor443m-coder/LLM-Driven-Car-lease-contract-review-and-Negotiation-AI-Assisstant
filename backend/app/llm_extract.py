import os
import openai
import json

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_KEY:
    openai.api_key = OPENAI_KEY

SLA_PROMPT = """
You are an assistant that extracts key SLA/contract fields from a car lease/loan contract text.
Return JSON with keys: apr, term_months, monthly_payment, down_payment, residual_value,
mileage_allowance_per_year, overage_fee_per_mile, early_termination_clause, buyout_price, red_flags (list).

Text:
---
{contract_text}
---
Return only valid JSON.
"""

def extract_sla_from_text(contract_text):
    if not OPENAI_KEY:
        return {
            "apr": None,
            "term_months": None,
            "monthly_payment": None,
            "down_payment": None,
            "residual_value": None,
            "mileage_allowance_per_year": None,
            "overage_fee_per_mile": None,
            "early_termination_clause": None,
            "buyout_price": None,
            "red_flags": []
        }

    prompt = SLA_PROMPT.format(contract_text=contract_text[:3000])
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    text = resp.choices[0].message.content
    try:
        return json.loads(text)
    except:
        return {"raw": text}
