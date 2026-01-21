def calculate_fair_monthly_lease(
    msrp: float,
    residual_value: float,
    lease_term_months: int,
    apr: float
) -> dict:
    """
    Finance-accurate lease pricing calculation.
    """

    # Money factor approximation
    money_factor = apr / 2400

    depreciation_fee = (msrp - residual_value) / lease_term_months
    finance_fee = (msrp + residual_value) * money_factor

    base_monthly = depreciation_fee + finance_fee

    return {
        "lease_term_months": lease_term_months,
        "apr": apr,
        "money_factor": round(money_factor, 6),
        "depreciation_fee": round(depreciation_fee, 2),
        "finance_fee": round(finance_fee, 2),
        "fair_monthly_lease": round(base_monthly, 2)
    }
