import re
from typing import List, Dict, Optional, Any
import json
import openai
from typing import Dict, Any

class LLMExtractor:
    def __init__(self, api_key=None):
        self.api_key = api_key
        # For demo, we'll use simulated responses
        self.sample_responses = {
            "interest_rate": "5.9%",
            "monthly_payment": "$450",
            "lease_term": "36 months",
            "down_payment": "$2,500",
            "mileage_limit": "12,000 miles/year",
            "excess_mileage_charge": "$0.25 per mile",
            "early_termination_fee": "$350",
            "purchase_option": "$15,000",
            "warranty": "3 years/36,000 miles",
            "insurance_required": "Comprehensive coverage with $500 deductible"
        }
    
    def extract_sla_terms(self, contract_text: str) -> Dict[str, Any]:
        """Extract SLA terms using LLM (simulated for demo)"""
        # In real implementation, this would call OpenAI API
        
        return {
            "extracted_terms": self.sample_responses,
            "red_flags": self._find_red_flags(contract_text),
            "fairness_score": self._calculate_fairness_score(contract_text),
            "recommendations": self._generate_recommendations()
        }
    
    def _find_red_flags(self, text: str) -> List[str]:
        """Identify potential red flags in contract"""
        red_flags = []
        text_lower = text.lower()
        
        red_flag_patterns = [
            ("excessive early termination", r"early termination fee.*?\$\d{4,}"),
            ("high excess mileage", r"excess mileage.*?\$0\.(3[0-9]|[4-9]\d)"),
            ("hidden fees", r"(?:admin|processing|document).*?fee.*?\$\d{2,}"),
            ("variable interest", r"variable.*?interest.*?rate"),
            ("balloon payment", r"balloon.*?payment"),
        ]
        
        for flag_name, pattern in red_flag_patterns:
            if re.search(pattern, text_lower):
                red_flags.append(flag_name)
        
        return red_flags
    
    def _calculate_fairness_score(self, text: str) -> int:
        """Calculate contract fairness score (0-100)"""
        score = 75  # Base score
        
        # Adjust based on red flags
        red_flags = self._find_red_flags(text)
        score -= len(red_flags) * 10
        
        # Check for favorable terms
        favorable_terms = [
            "warranty included",
            "gap insurance included",
            "maintenance included",
            "purchase option"
        ]
        
        for term in favorable_terms:
            if term in text.lower():
                score += 5
        
        return max(0, min(100, score))
    
    def _generate_recommendations(self) -> List[str]:
        """Generate negotiation recommendations"""
        return [
            "Negotiate for lower excess mileage charge (target: $0.15/mile)",
            "Request gap insurance to be included",
            "Ask for first month payment waiver",
            "Propose 10,000 miles/year instead of 12,000 if you drive less",
            "Request maintenance package inclusion"
        ]