import json
from llm import call_groq


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_prompt(contract_data: dict, explanation_data: dict, user_question: str) -> str:
    return f"""
You are an expert in car lease contracts, finance, and negotiation.

Below is the extracted contract data:
{json.dumps(contract_data, indent=2)}

Below is an expert explanation of the contract:
{json.dumps(explanation_data, indent=2)}

RULES:
- Answer ONLY using the information above.
- If something is not mentioned, say clearly that it is not specified.
- Be clear, professional, and practical.

User Question:
{user_question}

Answer:
"""


def run_chatbot():
    print("📄 Loading contract data...")
    contract_data = load_json("extracted_contract.json")
    explanation_data = load_json("llm_explanation.json")

    print("🤖 Car Lease Contract Chatbot")
    print("Type 'exit' to quit.\n")

    while True:
        user_question = input("You: ").strip()

        if user_question.lower() == "exit":
            print("Goodbye 👋")
            break

        prompt = build_prompt(contract_data, explanation_data, user_question)
        answer = call_groq(prompt)

        print("\nBot:", answer, "\n")


if __name__ == "__main__":
    run_chatbot()