import re

def normalize(text):
    return re.sub(r"[^a-z ]", "", text.lower())

def chatbot_response(user_input, data):
    q = normalize(user_input)

    fields = data["fields"]
    fairness_score = data["fairness_score"]
    fairness_reasons = data["fairness_reasons"]
    negotiation_tips = data["negotiation_tips"]
    vehicle = data["vehicle"]
    recall = data["recall"]

    if "fair" in q or "worth" in q:
        return f"Fairness score is {fairness_score}/100. Reasons: {', '.join(fairness_reasons)}"

    if "interest" in q or "apr" in q:
        return f"The interest rate (APR) is {fields.get('interest_rate')}%."

    if "payment" in q:
        return f"The monthly payment is ${fields.get('monthly_payment')}."

    if "negotiate" in q or "reduce" in q:
        if negotiation_tips:
            return "Negotiation tips: " + " ".join(negotiation_tips)
        return "No strong negotiation points found."

    if "vehicle" in q or "car" in q:
        return f"The vehicle is a {vehicle.get('Model Year')} {vehicle.get('Make')} {vehicle.get('Model')}."

    if "recall" in q:
        return recall.get("recall_summary")

    return "Ask about fairness, payments, interest rate, negotiation, vehicle, or recalls."
