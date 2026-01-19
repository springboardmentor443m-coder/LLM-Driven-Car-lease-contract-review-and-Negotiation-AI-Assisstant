def estimate_price(
    loan_amount,
    interest_rate,
    tenure_years,
    emi,
    mileage_per_year,
    residual_value=None
):
    months = tenure_years * 12
    total_paid = emi * months

    interest_paid = total_paid - loan_amount

    # If residual value not found, estimate (30% of loan amount)
    if residual_value is None:
        residual_value = loan_amount * 0.30

    # Approx vehicle price
    estimated_vehicle_price = loan_amount + interest_paid

    # Total miles
    total_miles = mileage_per_year * tenure_years
    cost_per_mile = estimated_vehicle_price / total_miles

    return {
        "estimated_vehicle_price": round(estimated_vehicle_price, 2),
        "total_paid": round(total_paid, 2),
        "interest_paid": round(interest_paid, 2),
        "residual_value": round(residual_value, 2),
        "cost_per_mile": round(cost_per_mile, 2)
    }
