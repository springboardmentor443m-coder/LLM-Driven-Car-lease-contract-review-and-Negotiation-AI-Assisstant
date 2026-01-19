import re

def analyze_contract(text):
    analysis = {}

    duration_match = re.search(r'(\d+)\s*(months|years)', text, re.IGNORECASE)
    analysis["lease_duration"] = duration_match.group(0) if duration_match else "Not found"

    payment_match = re.search(r'\$\s?\d+(?:,\d{3})*(?:\.\d{2})?', text)
    analysis["monthly_payment"] = payment_match.group(0) if payment_match else "Not found"

    mileage_match = re.search(r'(\d{4,6})\s*miles', text, re.IGNORECASE)
    analysis["mileage_limit"] = mileage_match.group(0) if mileage_match else "Not found"

    penalty_match = re.search(r'late fee|penalty|fine', text, re.IGNORECASE)
    analysis["penalty_clause"] = "Present" if penalty_match else "Not found"

    return analysis
