def calculate_fairness(llm_data):
    score = 100
    warnings = []

    apr = llm_data.get("APR")
    mileage = llm_data.get("Mileage_Limit")
    monthly_payment = llm_data.get("Monthly_Payment")

    # APR check
    if apr:
        try:
            apr_value = float(apr.replace("%", "").strip())
            if apr_value > 9:
                score -= 20
                warnings.append("High APR detected")
        except:
            pass

    # Mileage check
    if mileage:
        try:
            mileage_value = int(''.join(filter(str.isdigit, mileage)))
            if mileage_value < 10000:
                score -= 15
                warnings.append("Low mileage limit")
        except:
            pass

    # Monthly payment check
    if monthly_payment:
        try:
            payment_value = int(''.join(filter(str.isdigit, monthly_payment)))
            if payment_value > 50000:   # demo logic
                score -= 10
                warnings.append("High monthly payment")
        except:
            pass

    if score < 0:
        score = 0

    return {
        "Fairness_Score": score,
        "Warnings": warnings
    }