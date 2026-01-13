from groq import Groq
import re
import os
import json

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_lease_details(text):

    prompt = f"""
Extract ALL available lease and vehicle details from the contract.
Return ONLY valid JSON.

Lease Fields:
- APR
- Lease_Term
- Monthly_Payment
- Mileage_Limit
- Lease_Start_Date
- Lease_End_Date

Vehicle Fields (VERY IMPORTANT):
- Vehicle_VIN
- Vehicle_Make
- Vehicle_Model
- Vehicle_Year
- Vehicle_Body_Type
- Fuel_Type

Rules:
- If a field is not found, set it to null
- Do NOT guess
- Do NOT add extra text

Contract Text:
{text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Return valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    raw_output = response.choices[0].message.content

    match = re.search(r"\{.*\}", raw_output, re.DOTALL)

    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}
    return {}