from transformers import pipeline

# Load lightweight model (fast & free)
from transformers import pipeline

chatbot_pipeline = pipeline(
    "text2text-generation",
    model="google/flan-t5-small",
    max_length=256
)

def chatbot_response(user_question, contract_text, vehicle_data=None):
    """
    Context-aware chatbot for lease contracts
    """

    vehicle_context = ""
    if vehicle_data:
        vehicle_context = f"""
Vehicle Details:
Make: {vehicle_data.get('Make')}
Model: {vehicle_data.get('Model')}
Year: {vehicle_data.get('ModelYear')}
Fuel: {vehicle_data.get('FuelTypePrimary')}
"""

    prompt = f"""
You are an expert car lease assistant.

Use the contract and vehicle details to answer clearly.

Contract:
{contract_text}

{vehicle_context}

User Question:
{user_question}

Answer:
"""

    result = chatbot_pipeline(prompt)
    return result[0]["generated_text"]
