def answer_question(question, data):
    """
    ONE QUESTION → ONE ANSWER
    question : user question (string)
    data     : LAST_RESULT from app.py
    """

    q = question.lower()

    lease = data.get("lease", {})
    vin = data.get("vin", {})
    fairness = data.get("fairness", {})

    if "lease term" in q:
        return f"The lease term is {lease.get('Lease_Term', 'not available')} months."

    elif "monthly" in q or "payment" in q:
        return f"The monthly payment is ₹{lease.get('Monthly_Payment', 'not available')}."

    elif "mileage" in q:
        return f"The mileage limit is {lease.get('Mileage_Limit', 'not specified')} km."

    elif "vin" in q:
        return f"The vehicle VIN is {vin.get('VIN', 'not available')}."

    elif "model" in q:
        return f"The vehicle model is {vin.get('Model', 'not available')}."

    elif "make" in q:
        return f"The vehicle make is {vin.get('Make', 'not available')}."

    elif "year" in q:
        return f"The vehicle year is {vin.get('Year', 'not available')}."

    elif "fair" in q or "fairness" in q:
        return f"The contract fairness score is {fairness.get('Fairness_Score', 0)} out of 100."

    elif "negotiate" in q or "reduce" in q:
        return (
            "You can negotiate by requesting a lower monthly payment, "
            "higher mileage limit, or removal of extra charges."
        )

    else:
        return (
            "I can answer questions about lease term, monthly payment, "
            "mileage limit, VIN details, fairness score, and negotiation tips."
        )