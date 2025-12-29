import re
import requests

def extract_fields(text):
    patterns = {
        "interest_rate": r"Interest Rate\s*\(APR\)\s*:\s*([0-9]+(?:\.[0-9]+)?)",
        "monthly_payment": r"Monthly Payment\s*:\s*\$?([0-9,]+)",
        "down_payment": r"Down Payment\s*:\s*\$?([0-9,]+)",
        "mileage_allowance": r"Mileage Allowance\s*:\s*([0-9,]+)",
        "early_termination_fee": r"Early Termination Fee\s*:\s*\$?([0-9,]+)",
        "vin": r"\b([A-HJ-NPR-Z0-9]{17})\b"
    }

    fields = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fields[key] = match.group(1).replace(",", "")
    return fields


def calculate_fairness_score(fields):
    score = 100
    reasons = []

    apr = float(fields.get("interest_rate", 0))
    payment = float(fields.get("monthly_payment", 0))
    mileage = float(fields.get("mileage_allowance", 20000))

    if apr > 7:
        score -= 15
        reasons.append("Interest rate is above average.")

    if payment > 500:
        score -= 10
        reasons.append("Monthly payment is high.")

    if mileage < 12000:
        score -= 10
        reasons.append("Mileage allowance is low.")

    if not reasons:
        reasons.append("Contract terms are within standard market range.")

    return score, reasons


def negotiation_advice(fields):
    tips = []
    if float(fields.get("interest_rate", 0)) > 7:
        tips.append("APR is high. Try negotiating a lower interest rate.")
    if float(fields.get("monthly_payment", 0)) > 500:
        tips.append("Monthly payment is high. Ask for better terms.")
    return tips


def generate_summary(fields, fairness_score, negotiation_tips):
    summary = (
        f"This lease includes a monthly payment of ${fields.get('monthly_payment')} "
        f"with an interest rate of {fields.get('interest_rate')}%.\n\n"
        f"Fairness Score: {fairness_score}/100.\n\n"
    )
    if negotiation_tips:
        summary += "Negotiation Suggestions: " + " ".join(negotiation_tips)
    else:
        summary += "No major negotiation points identified."
    return summary


def vin_lookup(vin):
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json"
    r = requests.get(url).json()
    vehicle = {}
    for item in r["Results"]:
        if item["Variable"] in ["Make", "Model", "Model Year"]:
            vehicle[item["Variable"]] = item["Value"]
    return vehicle


def get_recall_info_by_vin(vin):
    return {
        "recall_summary": "Recall data unavailable (public API limitation)."
    }
