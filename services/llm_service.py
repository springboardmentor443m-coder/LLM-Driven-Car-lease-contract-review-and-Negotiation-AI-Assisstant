import os
import openai
from dotenv import load_dotenv


load_dotenv()


openai.api_key = os.getenv("OPENAI_API_KEY")


def extract_sla_from_contract(contract_text):
    """
    Extract SLA details from car lease / loan contract text using LLM
    """

    prompt = f"""
    You are an AI assistant specialized in car lease and loan contract analysis.

    From the contract text below, extract the following details and return
    the result strictly in JSON format.

    Fields to extract:
    - APR (interest rate)
    - Lease Term
    - Monthly Payment
    - Down Payment
    - Mileage Allowance
    - Early Termination Clause
    - Purchase Option / Buyout Price
    - Penalties or Late Fees

    Contract Text:
    \"\"\"{contract_text}\"\"\"

    Return JSON only. Do not add explanations.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a contract analysis assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    sla_json = response.choices[0].message.content
    return sla_json
