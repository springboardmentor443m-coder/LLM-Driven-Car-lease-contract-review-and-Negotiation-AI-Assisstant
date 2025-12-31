import re

def extract_fields(text):
    patterns = {
        "interest_rate": r"Interest Rate.*?([0-9]+(?:\.[0-9]+)?)",
        "monthly_payment": r"Monthly Payment.*?\$?([0-9,]+)",
        "mileage_allowance": r"Mileage.*?([0-9,]+)",
        "vin": r"(?:Vehicle Identification Number\s*\(VIN\)|VIN)[^A-Z0-9]*([A-HJ-NPR-Z0-9]{17})"


    }

    fields = {}
    for k, p in patterns.items():
        m = re.search(p, text, re.IGNORECASE)
        if m:
            fields[k] = m.group(1).replace(",", "")
    return fields


def calculate_fairness_score(fields, market_price=None):
    score = 100
    reasons = []

    apr = float(fields.get("interest_rate", 0))
    payment = float(fields.get("monthly_payment", 0))

    if apr > 6:
        score -= 15
        reasons.append("APR is higher than market average.")

    if payment > 500:
        score -= 10
        reasons.append("Monthly payment is high.")

    if market_price and payment * 36 > market_price * 0.6:
        score -= 20
        reasons.append("Lease cost is high compared to vehicle value.")

    return score, reasons


def negotiation_advice(fields):
    tips = []
    if float(fields.get("interest_rate", 0)) > 6:
        tips.append("Negotiate for lower APR.")
    if float(fields.get("monthly_payment", 0)) > 500:
        tips.append("Ask for reduced monthly payment.")
    return tips
