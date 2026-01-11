class LeaseCalculator:
    @staticmethod
    def calculate_monthly_payment(car_price, lease_months=36, down_payment=0, credit_score=700, residual_percent=50):
        """
        Calculate monthly lease payment
        """
        # Adjust interest rate based on credit score
        if credit_score >= 750:
            interest_rate = 0.04  # Excellent credit
        elif credit_score >= 650:
            interest_rate = 0.06  # Good credit
        elif credit_score >= 550:
            interest_rate = 0.08  # Fair credit
        else:
            interest_rate = 0.12  # Poor credit
        
        # Convert residual percentage to decimal
        residual_decimal = residual_percent / 100
        
        # Calculate residual value
        residual_value = car_price * residual_decimal
        
        # Calculate depreciation
        depreciation = (car_price - residual_value - down_payment) / lease_months
        
        # Calculate finance charge
        finance_charge = (car_price + residual_value) * (interest_rate / 12)
        
        # Calculate monthly payment
        monthly_payment = depreciation + finance_charge
        
        # Add taxes and fees (approx 8%)
        monthly_with_tax = monthly_payment * 1.08
        
        return {
            'monthly_payment': round(monthly_payment, 2),
            'monthly_with_tax': round(monthly_with_tax, 2),
            'total_cost': round(monthly_with_tax * lease_months, 2),
            'residual_value': round(residual_value, 2),
            'interest_rate': interest_rate
        }
    
    @staticmethod
    def calculate_affordability(monthly_income, monthly_expenses, desired_car_payment):
        """
        Calculate if lease is affordable
        """
        disposable_income = monthly_income - monthly_expenses
        affordability_ratio = (desired_car_payment / disposable_income) * 100
        
        if affordability_ratio <= 15:
            status = "Very Affordable"
            color = "green"
        elif affordability_ratio <= 25:
            status = "Affordable"
            color = "blue"
        elif affordability_ratio <= 35:
            status = "Moderate"
            color = "orange"
        else:
            status = "Not Affordable"
            color = "red"
        
        return {
            'disposable_income': disposable_income,
            'affordability_ratio': round(affordability_ratio, 2),
            'status': status,
            'color': color
        }