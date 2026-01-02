"""
Phase 6: Contract Fairness Scoring Engine
100% SAFE – handles bad DB + LLM data
"""

from typing import Dict


def safe_float(value, default=0.0):
    try:
        if value in [None, "", "Unknown"]:
            return default
        return float(value)
    except Exception:
        return default


def safe_int(value, default=0):
    try:
        if value in [None, "", "Unknown"]:
            return default
        return int(value)
    except Exception:
        return default


def evaluate_contract_fairness(sla: Dict) -> Dict:
    score = 100
    risks = []

    apr = safe_float(sla.get("apr"))
    mileage = safe_int(sla.get("mileage_limit"))
    payment = safe_float(sla.get("monthly_payment"))

    penalties = sla.get("penalties") or "Unknown"
    early_termination = sla.get("early_termination") or "Unknown"

    # ---------- RULES ----------
    if apr > 10:
        score -= 20
        risks.append("High interest rate")

    if mileage != 0 and mileage < 12000:
        score -= 10
        risks.append("Low mileage limit")

    if payment > 700:
        score -= 15
        risks.append("High monthly payment")

    if penalties != "Unknown":
        score -= 10
        risks.append("Strict penalty clauses")

    if early_termination != "Unknown":
        score -= 10
        risks.append("Early termination charges")

    score = max(0, min(score, 100))

    if score >= 75:
        risk_level = "Low"
    elif score >= 50:
        risk_level = "Medium"
    else:
        risk_level = "High"

    return {
        "fairness_score": score,
        "risk_level": risk_level,
        "risk_factors": risks,
        "summary": "Contract appears fair" if risk_level == "Low"
        else "Contract has notable risks"
    }
