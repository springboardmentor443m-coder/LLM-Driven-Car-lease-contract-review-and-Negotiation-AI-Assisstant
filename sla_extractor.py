import openai
import json
import re
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

load_dotenv()

class SLAExtractor:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        openai.api_key = self.api_key
        self.model = "gpt-3.5-turbo"  # or "gpt-4" for better accuracy
        
    def extract_sla(self, contract_text: str) -> Dict[str, Any]:
        """Extract SLA parameters from contract text using LLM"""
        
        prompt = f"""
        Extract the following key terms from this car lease/loan contract:
        
        {contract_text[:4000]}  # Limit text to avoid token limits
        
        Extract and return as JSON with these fields:
        1. interest_rate (APR percentage)
        2. lease_term_months
        3. monthly_payment_amount
        4. down_payment_amount
        5. residual_value
        6. mileage_allowance_per_year
        7. mileage_overage_charge_per_mile
        8. early_termination_conditions
        9. purchase_option_price
        10. maintenance_responsibilities
        11. warranty_coverage
        12. late_fee_amount
        13. penalty_clauses
        14. insurance_requirements
        
        If a field cannot be found, set it to null.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a contract analysis expert. Extract precise numerical values and terms from contracts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content
            
            # Parse JSON from response
            # Sometimes GPT returns text before/after JSON
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                sla_data = json.loads(json_match.group())
            else:
                sla_data = self._fallback_extraction(contract_text)
                
            return sla_data
            
        except Exception as e:
            print(f"Error in LLM extraction: {e}")
            return self._fallback_extraction(contract_text)
    
    def _fallback_extraction(self, text: str) -> Dict[str, Any]:
        """Fallback regex-based extraction if LLM fails"""
        patterns = {
            'interest_rate': r'APR\s*[:=]?\s*([\d\.]+)%',
            'monthly_payment': r'(?:monthly payment|payment amount)\s*[:=]?\s*\$?([\d,]+\.?\d*)',
            'lease_term': r'lease term\s*[:=]?\s*(\d+)\s*(?:months|years?)',
            'mileage_allowance': r'mileage[\s\S]*?(\d+,\d+|\d+)\s*miles',
        }
        
        sla_data = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                sla_data[key] = match.group(1)
            else:
                sla_data[key] = None
                
        return sla_data
    
    def calculate_fairness_score(self, sla_data: Dict, vehicle_data: Dict) -> float:
        """Calculate contract fairness score (0-100)"""
        score = 70  # Base score
        
        # Adjust based on various factors
        if sla_data.get('interest_rate'):
            apr = float(sla_data['interest_rate'])
            if apr > 8:
                score -= 20
            elif apr < 4:
                score += 10
        
        if sla_data.get('monthly_payment_amount'):
            payment = float(sla_data['monthly_payment_amount'])
            market_value = vehicle_data.get('pricing', {}).get('average_price', 0)
            if market_value > 0:
                expected_payment = market_value / 60  # 5-year loan
                if payment > expected_payment * 1.2:
                    score -= 15
        
        # Check for red flags
        red_flags = self._identify_red_flags(sla_data)
        score -= len(red_flags) * 5
        
        return max(0, min(100, score))
    
    def _identify_red_flags(self, sla_data: Dict) -> List[str]:
        """Identify problematic contract terms"""
        red_flags = []
        
        if sla_data.get('interest_rate') and float(sla_data['interest_rate']) > 10:
            red_flags.append("High interest rate")
        
        if sla_data.get('mileage_overage_charge_per_mile'):
            charge = float(sla_data['mileage_overage_charge_per_mile'])
            if charge > 0.25:
                red_flags.append("High mileage overage charges")
        
        if "non-refundable" in str(sla_data.get('early_termination_conditions', '')).lower():
            red_flags.append("Non-refundable termination clause")
        
        return red_flags
    
    def compare_contracts(self, contracts: List[Dict]) -> Dict[str, Any]:
        """Compare multiple contracts"""
        comparison = {
            'contracts': contracts,
            'summary': {},
            'recommendations': []
        }
        
        # Find best terms
        if contracts:
            best_apr = min(float(c.get('interest_rate', 100)) for c in contracts)
            lowest_payment = min(float(c.get('monthly_payment_amount', 10000)) for c in contracts)
            
            comparison['summary'] = {
                'best_apr': best_apr,
                'lowest_monthly_payment': lowest_payment,
                'number_of_contracts': len(contracts)
            }
        
        return comparison