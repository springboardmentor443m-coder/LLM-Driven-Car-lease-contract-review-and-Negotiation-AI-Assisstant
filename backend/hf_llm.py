import requests

API_TOKEN = "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"

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

headers = {"Authorization": f"Bearer {API_TOKEN}"}

def ask_llm(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 300}
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        return f"LLM Error: {response.text}"

    return response.json()[0]["generated_text"]
