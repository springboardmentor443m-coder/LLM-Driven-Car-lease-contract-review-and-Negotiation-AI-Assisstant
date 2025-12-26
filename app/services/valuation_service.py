def evaluate_deal(dealer_price, market_avg):
    # Defensive check for missing data
    if market_avg <= 0:
        return {
            "deal_score": 0,
            "verdict": "Insufficient market data",
            "fair_price_range": "Not available",
            "price_difference_percent": 0
        }

    diff_percent = ((dealer_price - market_avg) / market_avg) * 100
    score = max(0, 100 - abs(diff_percent))

    if diff_percent <= -5:
        verdict = "Good Deal"
    elif abs(diff_percent) < 5:
        verdict = "Fair Deal"
    else:
        verdict = "Bad Deal"

    return {
        "deal_score": round(score, 1),
        "verdict": verdict,
        "fair_price_range": f"${int(market_avg * 0.95)} - ${int(market_avg * 1.05)}",
        "price_difference_percent": round(diff_percent, 2)
    }


def estimate_5yr_value(current_price):
    """
    Simple depreciation model:
    ~15% depreciation per year for 5 years
    """

    if current_price <= 0:
        return "Not available"

    depreciation_rate = 0.15
    value = current_price

    for _ in range(5):
        value *= (1 - depreciation_rate)

    return f"${int(value)}"
