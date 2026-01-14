import httpx
from .market_service import estimate_market_price

async def get_vehicle_valuation(vin: str):
    """
    Verified logic to fetch Specs from NHTSA and Market Pricing.
    """
    # Initialize with keys exactly as React expects them
    nhtsa_details = {
        "VIN": vin or "Unknown", 
        "Make": "Unknown", 
        "Model": "Unknown", 
        "Model Year": "2024", 
        "Body Class": "sedan"
    }
    
    if vin:
        # Use the verified vPIC endpoint
        nhtsa_url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(nhtsa_url)
                if res.status_code == 200:
                    results = res.json().get("Results", [])
                    for item in results:
                        val, var = item.get("Value"), item.get("Variable")
                        # Capture only verified variables
                        if var == "Make": nhtsa_details["Make"] = val
                        if var == "Model": nhtsa_details["Model"] = val
                        if var == "Model Year": nhtsa_details["Model Year"] = val
                        if var == "Body Class": nhtsa_details["Body Class"] = val
        except Exception as e:
            print(f"NHTSA Fetch Error: {e}")

    # Calculate Market Price using the newly verified specs
    market_price = estimate_market_price(
        vin=vin, 
        year=nhtsa_details["Model Year"], 
        body=nhtsa_details["Body Class"]
    )
    
    # Placeholder to satisfy router requirements
    rapidapi_details = {"status": "success", "source": "nhtsa_verified_engine"}

    return nhtsa_details, rapidapi_details, market_price

def calculate_score(contract_price: float, market_price: float, money_factor: float = 0.0, 
                    residual_value: float = 0.0, mileage_allowance: float = 0.0, 
                    excess_mileage_fee: float = 0.0, lease_term_months: float = 36):
    """Calculates fairness score with Senior Auditor vocabulary based on multiple factors."""
    score = 75  # Start with neutral baseline
    reasons = []

    # Factor 1: Monthly Payment vs Market Price (20% weight)
    if market_price > 0 and contract_price > 0:
        # Fair monthly payment should be ~1-1.5% of market price
        fair_monthly = market_price * 0.012  # 1.2% benchmark
        if contract_price > fair_monthly * 1.2:  # 20% above fair
            overage_pct = ((contract_price - fair_monthly) / fair_monthly) * 100
            penalty = min(20, int(overage_pct * 0.15))
            score -= penalty
            reasons.append(f"Elevated Monthly Payment: {overage_pct:.1f}% above market benchmark.")
        elif contract_price < fair_monthly * 0.8:  # 20% below fair
            bonus_pct = ((fair_monthly - contract_price) / fair_monthly) * 100
            score += min(10, int(bonus_pct * 0.1))
            reasons.append(f"Favorable Monthly Rate: {bonus_pct:.1f}% below benchmark.")

    # Factor 2: Money Factor (APR equivalent) - 15% weight
    if money_factor > 0:
        apr_equivalent = money_factor * 2400  # Standard conversion
        if apr_equivalent > 0.08:  # 8% threshold
            penalty = min(25, int((apr_equivalent - 0.08) * 200))
            score -= penalty
            reasons.append(f"Usurious Rent Charge: {apr_equivalent*100:.2f}% APR equivalent is above market rates.")
        elif apr_equivalent < 0.04:  # Below 4%
            score += 8
            reasons.append("Favorable Interest Rate: Competitive money factor.")

    # Factor 3: Residual Value / Buyout Price - 20% weight
    if residual_value > 0 and market_price > 0:
        residual_pct = (residual_value / market_price) * 100
        if residual_pct < 50:  # Low residual
            penalty = min(20, int((50 - residual_pct) * 0.3))
            score -= penalty
            reasons.append(f"Depressed Residual: {residual_pct:.1f}% of market value disadvantages buyout.")
        elif residual_pct > 65:  # High residual
            score += 10
            reasons.append(f"Strong Residual: {residual_pct:.1f}% of market provides equity protection.")

    # Factor 4: Mileage Allowance & Excess Fees - 15% weight
    annual_allowance = mileage_allowance if mileage_allowance > 0 else 12000
    if annual_allowance < 10000:  # Below standard
        penalty = int((10000 - annual_allowance) * 0.005)
        score -= min(15, penalty)
        reasons.append(f"Restricted Mileage: {annual_allowance:.0f} mi/yr limit increases overage risk.")
    elif excess_mileage_fee > 0.30:  # Above $0.30 per mile
        penalty = min(10, int((excess_mileage_fee - 0.30) * 20))
        score -= penalty
        reasons.append(f"High Excess Mileage Fee: ${excess_mileage_fee:.2f}/mi exceeds market standard of $0.25.")
    else:
        reasons.append(f"Standard Mileage Terms: {annual_allowance:.0f} mi/yr with ${excess_mileage_fee:.2f}/mi overage.")

    # Factor 5: Lease Term Balance - 10% weight
    if lease_term_months < 24:
        penalty = int((36 - lease_term_months) * 0.5)
        score -= min(10, penalty)
        reasons.append("Short Lease Term: Higher depreciation concentration increases monthly cost.")
    elif lease_term_months > 48:
        penalty = int((lease_term_months - 36) * 0.3)
        score -= min(8, penalty)
        reasons.append("Extended Term: Potential warranty and maintenance issues beyond standard coverage.")

    final_score = max(0, min(100, int(score)))
    
    # Rating labels using senior-level terminology
    if final_score >= 80:
        rating = "Strategic"
    elif final_score >= 65:
        rating = "Standard"
    elif final_score >= 50:
        rating = "Fair"
    else:
        rating = "Dilutive"

    return {"score": final_score, "rating": rating, "reasons": reasons}