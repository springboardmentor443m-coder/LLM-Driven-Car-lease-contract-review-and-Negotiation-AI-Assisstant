"""
Phase 6: Contract Quality Analysis Engine
Explainable Pros & Cons (NO fake scoring)
100% SAFE – handles bad DB + LLM data
"""

from typing import Dict, List


# ======================================================
# SAFE CAST HELPERS
# ======================================================
def safe_float(value, default=None):
    try:
        if value in [None, "", "Unknown"]:
            return default
        return float(value)
    except Exception:
        return default


def safe_int(value, default=None):
    try:
        if value in [None, "", "Unknown"]:
            return default
        return int(float(value))
    except Exception:
        return default


# ======================================================
# PHASE 6 MAIN FUNCTION
# ======================================================
def evaluate_contract_fairness(sla: Dict) -> Dict:
    """
    Returns explainable contract pros & cons instead of fake numeric scores
    """

    pros: List[str] = []
    cons: List[str] = []
    negotiation_points: List[str] = []

    apr = safe_float(sla.get("apr"))
    mileage = safe_int(sla.get("mileage_limit"))
    payment = safe_float(sla.get("monthly_payment"))

    penalties = sla.get("penalties") or "Unknown"
    early_termination = sla.get("early_termination") or "Unknown"

    # ======================================================
    # APR ANALYSIS
    # ======================================================
    if apr is not None:
        if apr <= 7:
            pros.append("Interest rate is competitive for current market")
        elif apr <= 10:
            pros.append("Interest rate is within acceptable market range")
            negotiation_points.append("Ask if APR can be reduced slightly")
        else:
            cons.append("Interest rate is higher than market average")
            negotiation_points.append("Negotiate lower APR or better financing terms")
    else:
        cons.append("Interest rate not clearly specified")

    # ======================================================
    # MILEAGE ANALYSIS
    # ======================================================
    if mileage is not None:
        if mileage >= 15000:
            pros.append("High annual mileage allowance")
        elif mileage >= 12000:
            pros.append("Standard mileage allowance")
        else:
            cons.append("Low mileage limit may cause excess usage charges")
            negotiation_points.append("Request higher mileage allowance or lower excess-mile fees")
    else:
        cons.append("Mileage limit not specified")

    # ======================================================
    # PAYMENT ANALYSIS
    # ======================================================
    if payment is not None:
        if payment <= 500:
            pros.append("Monthly payment appears affordable")
        elif payment <= 800:
            pros.append("Monthly payment is moderate")
            negotiation_points.append("Ask for payment restructuring or longer tenure")
        else:
            cons.append("High monthly payment burden")
            negotiation_points.append("Negotiate lower EMI or extended tenure")
    else:
        cons.append("Monthly payment not clearly defined")

    # ======================================================
    # PENALTIES
    # ======================================================
    if penalties == "Unknown":
        pros.append("No explicit penalty clauses detected")
    else:
        cons.append("Penalty clauses are present and may increase cost")
        negotiation_points.append("Clarify penalty conditions and request softer terms")

    # ======================================================
    # EARLY TERMINATION
    # ======================================================
    if early_termination == "Unknown":
        pros.append("No early termination charges detected")
    else:
        cons.append("Early termination may incur significant charges")
        negotiation_points.append("Negotiate reduced early termination penalties")

    # ======================================================
    # SUMMARY LOGIC
    # ======================================================
    if not cons:
        summary = "Contract terms appear balanced with no major red flags"
        risk_level = "Low"
    elif len(cons) <= 2:
        summary = "Contract has some negotiable areas but no severe risks"
        risk_level = "Medium"
    else:
        summary = "Contract contains multiple unfavorable terms requiring negotiation"
        risk_level = "High"

    return {
        "risk_level": risk_level,
        "pros": pros,
        "cons": cons,
        "negotiation_opportunities": negotiation_points,
        "summary": summary
    }
