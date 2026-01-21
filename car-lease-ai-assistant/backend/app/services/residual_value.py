def calculate_residual_value(
    msrp: float,
    year: int,
    mileage: float,
    condition: str = "good",
    current_year: int = 2025
) -> dict:
    """
    Finance-grade residual value calculation.
    """

    age_years = max(0, current_year - year)

    # Baseline depreciation (industry-style)
    depreciation_rate = 0.15  # 15% per year
    baseline_value = msrp * ((1 - depreciation_rate) * age_years)

    # Condition factor
    condition_factors = {
        "excellent": 0.98,
        "good": 0.92,
        "fair": 0.85,
        "poor": 0.75
    }
    condition_factor = condition_factors.get(condition.lower(), 0.92)

    # Mileage adjustment
    expected_mileage = age_years * 12000
    mileage_diff = mileage - expected_mileage

    if mileage_diff <= 0:
        mileage_factor = 1.0
    else:
        mileage_factor = max(0.80, 1 - (mileage_diff / 100000))

    final_value = baseline_value * condition_factor * mileage_factor

    return {
        "year": year,
        "age_years": age_years,
        "msrp": msrp,
        "baseline_value": round(baseline_value, 2),
        "condition": condition,
        "condition_factor": condition_factor,
        "mileage": mileage,
        "mileage_factor": round(mileage_factor, 3),
        "final_value": round(final_value, 2)
    }
