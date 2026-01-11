import random
from typing import List, Dict

class NegotiationAssistant:
    def __init__(self):
        self.negotiation_strategies = [
            "Focus on the monthly payment first, then discuss other terms",
            "Mention competitor offers to create leverage",
            "Ask for value-added services instead of price reduction",
            "Use the 'walk-away' power if terms are not favorable",
            "Bundle multiple services for better pricing"
        ]
        
        self.sample_responses = {
            "high_interest": [
                "I've seen better rates at other dealerships. Can you match 4.9% APR?",
                "My credit score is excellent. I believe I qualify for your best rate.",
                "Could you explain why the rate is higher than market average?"
            ],
            "high_down_payment": [
                "Is it possible to reduce the down payment and increase monthly slightly?",
                "I've seen offers with $0 down. Can we work on this?",
                "Let's discuss alternative down payment options."
            ],
            "mileage_limit": [
                "I drive less than 10,000 miles annually. Can we adjust the limit?",
                "What's the cost to increase mileage allowance?",
                "Can we negotiate the excess mileage charge?"
            ],
            "early_termination": [
                "The early termination fee seems high. Can we reduce it?",
                "What if I want to upgrade early? Are there options?",
                "Can we discuss more flexible termination terms?"
            ]
        }
    
    def generate_response(self, issue_type: str, context: Dict = None) -> str:
        """Generate negotiation response based on issue type"""
        if issue_type in self.sample_responses:
            return random.choice(self.sample_responses[issue_type])
        
        return "I'd like to negotiate better terms on this. Can we discuss?"
    
    def get_negotiation_tips(self, contract_terms: Dict) -> List[str]:
        """Get personalized negotiation tips based on contract terms"""
        tips = []
        
        # Check interest rate
        if contract_terms.get('apr', 0) > 6:
            tips.append("Interest rate is above market average. Target 4-5% range.")
        
        # Check down payment
        if contract_terms.get('down_payment', 0) > 3000:
            tips.append("Down payment seems high. Try to negotiate under $2,000.")
        
        # Check mileage
        if contract_terms.get('mileage_limit', 12000) < 10000:
            tips.append("Mileage limit is low. Request at least 12,000 miles/year.")
        
        # Check early termination
        if contract_terms.get('early_termination_fee', 0) > 500:
            tips.append("Early termination fee is excessive. Aim for $300 or less.")
        
        return tips + self.negotiation_strategies
    
    def generate_email_template(self, dealer_name: str, issues: List[str]) -> str:
        """Generate negotiation email template"""
        email = f"""Dear {dealer_name},

I've reviewed the lease contract proposal and would like to discuss a few points:

"""
        
        for issue in issues[:3]:  # Limit to 3 main issues
            if "interest" in issue.lower():
                email += "- The interest rate seems higher than current market rates. Can we discuss a better rate?\n"
            elif "down payment" in issue.lower():
                email += "- The down payment amount is higher than I anticipated. Are there options to reduce this?\n"
            elif "mileage" in issue.lower():
                email += "- The mileage allowance may not suit my driving habits. Can we adjust this?\n"
            elif "termination" in issue.lower():
                email += "- The early termination terms seem restrictive. Can we make them more flexible?\n"
        
        email += """
I'm confident we can reach an agreement that works for both parties. Please let me know your thoughts.

Best regards,
[Your Name]
"""
        
        return email