import json
from chatbot import contract_chatbot

with open("extracted_contract.json") as f:
    contract_data = json.load(f)

chat_history = []

print("Car Lease Contract Chatbot (type 'exit' to quit)\n")

while True:
    question = input("You: ")
    if question.lower() == "exit":
        break

    # Keep only last 4 messages
    history_text = "\n".join(chat_history[-4:])

    answer = contract_chatbot(question, contract_data, history_text)

    print("\nBot:", answer, "\n")

    chat_history.append(f"User: {question}")
    chat_history.append(f"Bot: {answer}")
