# fairness_engine.py
"""
Calculate fairness score (0-100) based on contract terms.
Higher score = better deal for buyer.
"""

def calculate_fairness_score(structured_data: dict) -> tuple:
    """
    Returns (score: int, reasons: list[str])
    Score: 0-100, where 100 is best for buyer
    IMPROVED: More sensitive to unfair terms
    """
    score = 100
    reasons = []
    
    # Get nested data safely
    core = structured_data.get("core", {})
    financial = structured_data.get("financial_analysis", {})
    risk = structured_data.get("risk_analysis", {})
    
    # 1. Check APR / Interest Rate - MORE STRICT
    apr_str = core.get("apr", "") or core.get("interest_rate", "")
    if apr_str:
        try:
            apr_val = float(apr_str.replace("%", "").strip())
            if apr_val >= 20:
                score -= 40
                reasons.append(f"Extremely high APR: {apr_val}% (deduct 40 points)")
            elif apr_val >= 15:
                score -= 30
                reasons.append(f"Very high APR: {apr_val}% (deduct 30 points)")
            elif apr_val >= 10:
                score -= 20
                reasons.append(f"High APR: {apr_val}% (deduct 20 points)")
            elif apr_val >= 7:
                score -= 10
                reasons.append(f"Moderate APR: {apr_val}% (deduct 10 points)")
            elif apr_val >= 5:
                score -= 5
                reasons.append(f"Acceptable APR: {apr_val}% (deduct 5 points)")
        except:
            pass
    
    # 2. Check Money Factor (for leases) - ADDED
    money_factor = core.get("money_factor", "")
    if money_factor:
        try:
            mf_val = float(str(money_factor).strip())
            # Money factor to APR: multiply by 2400
            implied_apr = mf_val * 2400
            if implied_apr >= 10:
                score -= 25
                reasons.append(f"High money factor: {mf_val} (~{implied_apr:.1f}% APR) (deduct 25 points)")
            elif implied_apr >= 6:
                score -= 15
                reasons.append(f"Elevated money factor: {mf_val} (~{implied_apr:.1f}% APR) (deduct 15 points)")
        except:
            pass
    
    # 3. Check Documentation/Acquisition Fees - IMPROVED THRESHOLDS
    doc_fee = core.get("documentation_fee", "")
    if doc_fee:
        try:
            fee_val = float(doc_fee.replace("$", "").replace(",", "").strip())
            if fee_val > 1000:
                score -= 20
                reasons.append(f"Excessive documentation fee: ${fee_val} (deduct 20 points)")
            elif fee_val > 500:
                score -= 10
                reasons.append(f"High documentation fee: ${fee_val} (deduct 10 points)")
            elif fee_val > 200:  # Lower threshold - $200+ is notable
                score -= 5
                reasons.append(f"Moderate documentation fee: ${fee_val} (deduct 5 points)")
        except:
            pass
    
    acq_fee = core.get("acquisition_fee", "")
    if acq_fee:
        try:
            fee_val = float(acq_fee.replace("$", "").replace(",", "").strip())
            if fee_val > 1200:
                score -= 20
                reasons.append(f"Excessive acquisition fee: ${fee_val} (deduct 20 points)")
            elif fee_val > 800:
                score -= 10
                reasons.append(f"High acquisition fee: ${fee_val} (deduct 10 points)")
            elif fee_val > 400:  # Lower threshold
                score -= 5
                reasons.append(f"Moderate acquisition fee: ${fee_val} (deduct 5 points)")
        except:
            pass
    
    # 4. Check Disposition Fee (unfair if over $500)
    disp_fee = core.get("disposition_fee", "")
    if disp_fee:
        try:
            fee_val = float(disp_fee.replace("$", "").replace(",", "").strip())
            if fee_val > 500:
                score -= 15
                reasons.append(f"High disposition fee: ${fee_val} (deduct 15 points)")
        except:
            pass
    
    # 5. Check Excess Mileage Fee (unfair if over $0.25/mile)
    excess_mileage = core.get("excess_mileage_fee", "")
    if excess_mileage:
        try:
            # Extract numeric value
            fee_str = str(excess_mileage).replace("$", "").replace("per mile", "").replace("/mile", "").strip()
            fee_val = float(fee_str)
            if fee_val > 0.35:
                score -= 20
                reasons.append(f"Excessive mileage penalty: ${fee_val}/mile (deduct 20 points)")
            elif fee_val > 0.25:
                score -= 10
                reasons.append(f"High mileage penalty: ${fee_val}/mile (deduct 10 points)")
        except:
            pass
    
    # 6. Check Monthly Payment vs Vehicle Price ratio
    monthly = core.get("monthly_payment", "")
    vehicle_price = financial.get("vehicle_price", "") or core.get("vehicle_price", "") or core.get("msrp", "")
    
    if monthly and vehicle_price:
        try:
            monthly_val = float(monthly.replace("$", "").replace(",", "").strip())
            price_val = float(vehicle_price.replace("$", "").replace(",", "").strip())
            
            if price_val > 0:
                ratio = (monthly_val * 12) / price_val
                if ratio > 0.40:  # Paying >40% annually
                    score -= 20
                    reasons.append(f"Very high payment-to-price ratio: {ratio:.1%} annually (deduct 20 points)")
                elif ratio > 0.35:  # Paying >35% annually
                    score -= 15
                    reasons.append(f"High payment-to-price ratio: {ratio:.1%} annually (deduct 15 points)")
        except:
            pass
    
    # 7. Check Term Length - MORE STRICT
    term_months = core.get("term_months", "")
    if term_months:
        try:
            term_val = int(str(term_months).strip())
            if term_val > 84:  # More than 7 years
                score -= 25
                reasons.append(f"Extremely long term: {term_val} months (deduct 25 points)")
            elif term_val > 72:  # More than 6 years
                score -= 15
                reasons.append(f"Very long term: {term_val} months (deduct 15 points)")
            elif term_val > 60:  # More than 5 years
                score -= 10
                reasons.append(f"Long term: {term_val} months (deduct 10 points)")
        except:
            pass
    
    # 8. Check Down Payment
    down_payment = core.get("down_payment", "")
    if down_payment and vehicle_price:
        try:
            down_val = float(down_payment.replace("$", "").replace(",", "").strip())
            price_val = float(vehicle_price.replace("$", "").replace(",", "").strip())
            
            if price_val > 0:
                down_ratio = down_val / price_val
                if down_ratio < 0.05:  # Less than 5% down
                    score -= 15
                    reasons.append(f"Very low down payment: {down_ratio:.1%} (deduct 15 points)")
                elif down_ratio < 0.1:  # Less than 10% down
                    score -= 10
                    reasons.append(f"Low down payment: {down_ratio:.1%} (deduct 10 points)")
        except:
            pass
    
    # 9. Check other fees - IMPROVED: Check both count AND total amount
    other_fees = core.get("other_fees", [])
    if other_fees:
        fee_count = len(other_fees)
        
        # Calculate total of other fees
        total_other_fees = 0
        for fee_str in other_fees:
            try:
                # Extract numeric value from fee string
                fee_clean = str(fee_str).replace("$", "").replace(",", "").strip()
                # Handle list format like "['90', '425']"
                if "[" in fee_clean:
                    import re
                    numbers = re.findall(r'\d+', fee_clean)
                    for num in numbers:
                        total_other_fees += float(num)
                else:
                    total_other_fees += float(fee_clean)
            except:
                pass
        
        # Penalize by count
        if fee_count > 5:
            score -= 15
            reasons.append(f"Excessive additional fees ({fee_count} fees) (deduct 15 points)")
        elif fee_count > 3:
            score -= 10
            reasons.append(f"Multiple additional fees ({fee_count} fees) (deduct 10 points)")
        elif fee_count > 1:
            score -= 5
            reasons.append(f"Several additional fees ({fee_count} fees) (deduct 5 points)")
        
        # Penalize by total amount
        if total_other_fees > 1000:
            score -= 15
            reasons.append(f"High total additional fees: ${total_other_fees:.2f} (deduct 15 points)")
        elif total_other_fees > 500:
            score -= 10
            reasons.append(f"Significant additional fees: ${total_other_fees:.2f} (deduct 10 points)")
        elif total_other_fees > 200:
            score -= 5
            reasons.append(f"Moderate additional fees: ${total_other_fees:.2f} (deduct 5 points)")
    
    # 9b. Check TOTAL FEES vs Loan Amount (NEW - Important!)
    vehicle_price = financial.get("vehicle_price", "") or core.get("vehicle_price", "") or core.get("msrp", "")
    if vehicle_price:
        try:
            price_val = float(str(vehicle_price).replace("$", "").replace(",", "").strip())
            
            # Calculate total fees
            total_fees = 0
            if doc_fee:
                try:
                    total_fees += float(str(doc_fee).replace("$", "").replace(",", "").strip())
                except:
                    pass
            if acq_fee:
                try:
                    total_fees += float(str(acq_fee).replace("$", "").replace(",", "").strip())
                except:
                    pass
            if other_fees:
                for fee_str in other_fees:
                    try:
                        fee_clean = str(fee_str).replace("$", "").replace(",", "").strip()
                        if "[" in fee_clean:
                            import re
                            numbers = re.findall(r'\d+', fee_clean)
                            for num in numbers:
                                total_fees += float(num)
                        else:
                            total_fees += float(fee_clean)
                    except:
                        pass
            
            # Check fee-to-loan ratio
            if price_val > 0 and total_fees > 0:
                fee_ratio = total_fees / price_val
                if fee_ratio > 0.05:  # Fees > 5% of loan
                    score -= 20
                    reasons.append(f"Very high total fees: ${total_fees:.2f} ({fee_ratio:.1%} of loan amount) (deduct 20 points)")
                elif fee_ratio > 0.03:  # Fees > 3% of loan
                    score -= 15
                    reasons.append(f"High total fees: ${total_fees:.2f} ({fee_ratio:.1%} of loan amount) (deduct 15 points)")
                elif fee_ratio > 0.02:  # Fees > 2% of loan
                    score -= 10
                    reasons.append(f"Moderate total fees: ${total_fees:.2f} ({fee_ratio:.1%} of loan amount) (deduct 10 points)")
                elif total_fees > 500:  # Absolute amount check
                    score -= 5
                    reasons.append(f"Notable total fees: ${total_fees:.2f} (deduct 5 points)")
        except:
            pass
    
    # 10. Risk analysis integration - MORE WEIGHT
    high_risks = risk.get("high_risks", [])
    medium_risks = risk.get("medium_risks", [])
    
    if high_risks:
        deduction = len(high_risks) * 15  # Increased from 10
        score -= deduction
        reasons.append(f"{len(high_risks)} high-risk items identified (deduct {deduction} points)")
    
    if medium_risks:
        deduction = len(medium_risks) * 8  # Increased from 5
        score -= deduction
        reasons.append(f"{len(medium_risks)} medium-risk items identified (deduct {deduction} points)")
    
    # 11. Check contract type
    contract_type = core.get("contract_type", "").lower()
    if "rental" in contract_type:
        score -= 5
        reasons.append("Rental agreement (typically less favorable) (deduct 5 points)")
    
    # Ensure score stays within bounds
    score = max(0, min(100, score))
    
    # Add summary note at the beginning
    if score >= 85:
        reasons.insert(0, "✅ Excellent deal with very favorable terms")
    elif score >= 70:
        reasons.insert(0, "✓ Good deal with reasonable terms")
    elif score >= 55:
        reasons.insert(0, "⚠️ Average deal with some concerns")
    elif score >= 40:
        reasons.insert(0, "⚠️ Below average deal with multiple issues")
    else:
        reasons.insert(0, "❌ Poor deal with significant unfavorable terms")
    
    return score, reasons

    # ============================================================
# PUBLIC ENTRY POINT (USED BY STREAMLIT APP)
# ============================================================

def calculate_fairness(extracted: dict) -> tuple:
    """
    Wrapper used by Streamlit.
    Accepts full extraction output and returns (score, reasons).
    """
    structured = extracted.get("llm_structured_data_full") or extracted
    return calculate_fairness_score(structured)
