import requests

# 🔹 Paste your Hugging Face token here
API_TOKEN = "hf_your_real_token_here"

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}


def extract_sla(contract_text: str) -> str:
    """
    Extract SLA fields from car lease/loan contract text using a FREE open-source LLM.
    """

    prompt = f"""
You are an expert in car lease and loan contracts.

Extract the following fields from the contract text.
If a field is missing, return "Not Found".

Fields:
- APR
- Lease Term
- Monthly Payment
- Down Payment
- Mileage Limit
- Early Termination Fee
- Buyout Price

Return ONLY valid JSON.

Contract Text:
{contract_text}
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    # 🔹 Error handling
    if response.status_code != 200:
        return f"LLM Error: {response.text}"

    result = response.json()

    # HF returns list of responses
    return result[0]["generated_text"]
