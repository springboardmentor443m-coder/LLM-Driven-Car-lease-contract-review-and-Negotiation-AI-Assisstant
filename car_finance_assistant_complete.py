# car_finance_assistant_complete.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import re
import io
import random

# Set page configuration
st.set_page_config(
    page_title="Car Finance AI Assistant",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session states
session_defaults = {
    'messages': [],
    'contract_data': {},
    'multiple_contracts': [],
    'vin_lookup_result': None,
    'price_check_result': None,
    'comparison_result': None,
    'negotiation_advice': None,
    'affordability_result': None,
    'current_vin': '',
    'current_price': 0,
    'chat_history': []
}

for key, value in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

class CarFinanceAssistant:
    """Complete AI Assistant for Car Financing"""
    
    def __init__(self):
        self.vin_database = self._load_vin_database()
        self.market_data = self._load_market_data()
        self.industry_standards = self._load_industry_standards()
        
    def _load_vin_database(self):
        """Sample VIN database"""
        return {
            "1HGCM82633A123456": {
                "manufacturer": "Honda",
                "model": "Accord",
                "year": 2023,
                "safety_rating": "5-Star",
                "recall_history": "No active recalls",
                "vehicle_type": "Sedan",
                "msrp": 28000,
                "engine": "1.5L Turbo",
                "transmission": "CVT",
                "fuel_type": "Gasoline",
                "fuel_economy": "30 city / 38 highway"
            },
            "2T1BURHE8JC123456": {
                "manufacturer": "Toyota",
                "model": "Camry",
                "year": 2018,
                "safety_rating": "5-Star",
                "recall_history": "Recall: Airbag inflator (2019) - Repaired",
                "vehicle_type": "Sedan",
                "msrp": 24000,
                "engine": "2.5L 4-cylinder",
                "transmission": "8-Speed Automatic",
                "fuel_type": "Gasoline",
                "fuel_economy": "29 city / 41 highway"
            },
            "3FA6P0HD9MR123456": {
                "manufacturer": "Ford",
                "model": "Fusion",
                "year": 2021,
                "safety_rating": "4-Star",
                "recall_history": "No active recalls",
                "vehicle_type": "Sedan",
                "msrp": 25000,
                "engine": "1.5L EcoBoost",
                "transmission": "6-Speed Automatic",
                "fuel_type": "Gasoline",
                "fuel_economy": "27 city / 36 highway"
            },
            "5YJSA1E21MF123456": {
                "manufacturer": "Tesla",
                "model": "Model 3",
                "year": 2021,
                "safety_rating": "5-Star",
                "recall_history": "Recall: Camera calibration (2022) - Software update",
                "vehicle_type": "Electric Sedan",
                "msrp": 42000,
                "engine": "Electric Motor",
                "transmission": "Single Speed",
                "fuel_type": "Electric",
                "fuel_economy": "131 MPGe"
            },
            # Indian Vehicles
            "MA1PA24B8M1234567": {
                "manufacturer": "Mahindra",
                "model": "Scorpio",
                "year": 2023,
                "safety_rating": "4-Star",
                "recall_history": "No active recalls",
                "vehicle_type": "SUV",
                "msrp": 25000,
                "engine": "2.2L Diesel",
                "transmission": "Manual",
                "fuel_type": "Diesel",
                "fuel_economy": "15 km/l"
            },
            "MEX77123H1234567": {
                "manufacturer": "Maruti Suzuki",
                "model": "Swift",
                "year": 2022,
                "safety_rating": "3-Star",
                "recall_history": "No active recalls",
                "vehicle_type": "Hatchback",
                "msrp": 12000,
                "engine": "1.2L Petrol",
                "transmission": "Manual",
                "fuel_type": "Petrol",
                "fuel_economy": "22 km/l"
            }
        }
    
    def _load_market_data(self):
        """Market interest rates and pricing data"""
        return {
            "average_apr": {
                "new": {"excellent_credit": 3.5, "good_credit": 4.5, "fair_credit": 6.0, "poor_credit": 8.0},
                "used": {"excellent_credit": 4.0, "good_credit": 5.5, "fair_credit": 7.5, "poor_credit": 10.0},
                "lease": {"excellent_credit": 3.0, "good_credit": 4.0, "fair_credit": 5.5, "poor_credit": 8.0}
            },
            "processing_fee_range": {"min": 100, "max": 500, "average": 300},
            "down_payment_percent": {"recommended": 20, "minimum": 10, "average": 15}
        }
    
    def _load_industry_standards(self):
        """Industry standard ranges for various terms"""
        return {
            "apr_ranges": {
                "excellent": (0.0, 4.0),
                "good": (4.1, 6.0),
                "fair": (6.1, 9.0),
                "high": (9.1, 15.0),
                "predatory": (15.1, 100.0)
            },
            "term_months": {
                "new": [24, 36, 48, 60, 72],
                "used": [24, 36, 48, 60],
                "lease": [24, 36, 39, 48]
            },
            "mileage_limits": {
                "standard": 12000,
                "high": 15000,
                "unlimited": 99999
            },
            "disposition_fee": {
                "range": (300, 500),
                "average": 400
            },
            "early_termination": {
                "penalty_months": (1, 3),
                "fee_multiplier": (0.5, 2.0)
            }
        }
    
    # ========== VIN DECODER ==========
    
    def decode_vin(self, vin):
        """Universal VIN decoder"""
        vin = vin.upper().strip()
        
        if vin in self.vin_database:
            return self.vin_database[vin]
        
        # Intelligent estimation for unknown VINs
        return self._estimate_vehicle_from_vin(vin)
    
    def _estimate_vehicle_from_vin(self, vin):
        """Estimate vehicle details from VIN"""
        if len(vin) != 17:
            return {"error": "VIN must be 17 characters"}
        
        # Brand detection
        brand_map = {
            "1HG": "Honda", "2HG": "Honda", "JHM": "Honda",
            "1FA": "Ford", "2FA": "Ford", "1FM": "Ford",
            "WBA": "BMW", "WBS": "BMW", "WDB": "Mercedes",
            "JT": "Toyota", "JN": "Nissan", "JF": "Subaru",
            "KL": "Daewoo", "KM": "Hyundai", "KN": "Kia",
            "MA1": "Mahindra", "MA3": "Mahindra",
            "MBH": "Tata", "MEX": "Maruti Suzuki",
            "5YJ": "Tesla", "7SA": "Tesla"
        }
        
        manufacturer = "Unknown"
        country = "Global"
        
        for prefix, brand in brand_map.items():
            if vin.startswith(prefix):
                manufacturer = brand
                if prefix in ["MA1", "MA3", "MBH", "MEX"]:
                    country = "India"
                elif prefix in ["1HG", "1FA", "5YJ"]:
                    country = "USA"
                elif prefix in ["WBA", "WDB"]:
                    country = "Germany"
                elif prefix in ["JT", "JN"]:
                    country = "Japan"
                break
        
        # Year estimation
        year_codes = {
            "M": 2021, "N": 2022, "P": 2023, "R": 2024,
            "A": 2010, "B": 2011, "C": 2012, "D": 2013,
            "E": 2014, "F": 2015, "G": 2016, "H": 2017,
            "J": 2018, "K": 2019, "L": 2020
        }
        year = year_codes.get(vin[9], 2022)
        
        # Segment estimation
        segment = "Sedan"
        if vin[3] in ["2", "8"]:
            segment = "SUV" if vin[3] == "2" else "Hatchback"
        
        return {
            "country": country,
            "manufacturer": manufacturer,
            "model": f"{manufacturer} {segment}",
            "year": year,
            "engine": "Standard Engine",
            "fuel_type": "Petrol/Gasoline",
            "transmission": "Automatic/Manual",
            "segment": segment,
            "safety_rating": "Estimated",
            "recall_history": "Verify independently",
            "msrp": 25000 if country != "India" else 1500000,
            "note": "⚠️ Estimated from VIN pattern"
        }
    
    # ========== PRICE ANALYSIS ==========
    
    def analyze_price(self, vehicle_info, asking_price, currency="USD"):
        """Analyze if price is fair"""
        # Get base price
        if currency == "INR":
            base_price = vehicle_info.get('msrp', 1000000)
            symbol = "₹"
        else:
            base_price = vehicle_info.get('msrp', 25000)
            symbol = "$"
        
        # Adjust for condition
        condition_multiplier = {
            "excellent": 1.0,
            "good": 0.9,
            "fair": 0.8,
            "poor": 0.7
        }
        condition = vehicle_info.get('condition', 'good')
        adjusted_price = base_price * condition_multiplier.get(condition, 0.9)
        
        # Adjust for mileage
        mileage = vehicle_info.get('mileage', 0)
        if mileage > 0:
            if mileage <= 10000:
                mileage_factor = 1.0
            elif mileage <= 50000:
                mileage_factor = 0.9
            elif mileage <= 100000:
                mileage_factor = 0.8
            else:
                mileage_factor = 0.7
            adjusted_price *= mileage_factor
        
        # Calculate difference
        difference = asking_price - adjusted_price
        pct_diff = (difference / adjusted_price) * 100
        
        # Determine fairness
        if pct_diff > 20:
            fairness = "🚨 Seriously Overpriced"
            recommendation = "Walk away or negotiate 25%+ reduction"
            color = "red"
        elif pct_diff > 10:
            fairness = "⚠️ Overpriced"
            recommendation = "Negotiate 15-20% reduction"
            color = "orange"
        elif pct_diff < -20:
            fairness = "🎉 Excellent Deal"
            recommendation = "Buy immediately if vehicle checks out"
            color = "green"
        elif pct_diff < -10:
            fairness = "👍 Good Value"
            recommendation = "Good price, minor negotiation possible"
            color = "lightgreen"
        else:
            fairness = "✅ Fair Market Price"
            recommendation = "Standard price, negotiate 5-10%"
            color = "blue"
        
        return {
            "fairness": fairness,
            "recommendation": recommendation,
            "color": color,
            "details": {
                "market_price": round(base_price),
                "adjusted_price": round(adjusted_price),
                "asking_price": asking_price,
                "difference": round(difference),
                "percentage_difference": round(pct_diff, 1),
                "currency": currency,
                "symbol": symbol
            }
        }
    
    # ========== CONTRACT ANALYSIS ==========
    
    def extract_contract_data(self, text):
        """Extract all possible contract data from text"""
        data = {}
        
        # Clean and normalize text
        text = text.replace('\n', ' ').replace('\r', ' ').replace(',', '')
        
        # Define extraction patterns
        extraction_patterns = [
            ('apr', r'APR[\s:]*([\d\.]+)\s*%'),
            ('apr', r'annual percentage rate[\s:]*([\d\.]+)\s*%'),
            ('monthly_payment', r'monthly payment[\s:]*\$([\d\.]+)'),
            ('monthly_payment', r'emi[\s:]*\$([\d\.]+)'),
            ('total_amount', r'total amount[\s:]*\$([\d\.]+)'),
            ('down_payment', r'down payment[\s:]*\$([\d\.]+)'),
            ('duration', r'term[\s:]*(\d+)[\s]*months'),
            ('processing_fee', r'processing fee[\s:]*\$([\d\.]+)'),
            ('documentation_fee', r'documentation fee[\s:]*\$([\d\.]+)'),
        ]
        
        # Extract using patterns
        for key, pattern in extraction_patterns:
            if key not in data:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        value = float(match.group(1))
                        data[key] = value
                    except:
                        pass
        
        # Extract boolean flags
        flags = [
            ('has_early_termination', ['early termination', 'termination fee']),
            ('has_penalty_clause', ['penalty', 'late fee']),
            ('has_warranty', ['warranty', 'guarantee']),
            ('is_lease', ['lease', 'lessor']),
            ('is_loan', ['loan', 'financing']),
        ]
        
        for key, keywords in flags:
            for keyword in keywords:
                if keyword in text.lower():
                    data[key] = True
                    break
        
        return data
    
    def analyze_contract_complete(self, contract_data):
        """Complete analysis of contract with detailed scoring"""
        analysis = {
            "risk_level": "Low",
            "fairness_score": 10,
            "scoring_breakdown": {},
            "red_flags": [],
            "yellow_flags": [],
            "green_flags": [],
            "recommendations": [],
            "key_points": [],
            "missing_terms": [],
            "fraud_alerts": []
        }
        
        # Check for missing essential terms
        essential_terms = ['apr', 'monthly_payment', 'duration', 'total_amount']
        analysis['missing_terms'] = [term for term in essential_terms if term not in contract_data]
        
        if analysis['missing_terms']:
            analysis['fairness_score'] -= len(analysis['missing_terms']) * 0.5
            analysis['yellow_flags'].append(f"Missing essential terms: {', '.join(analysis['missing_terms'])}")
        
        # APR Analysis
        if 'apr' in contract_data:
            apr = contract_data['apr']
            apr_score = self._score_apr(apr)
            analysis['scoring_breakdown']['apr_score'] = apr_score
            analysis['fairness_score'] += (apr_score - 2.5)
            
            if apr > 25:
                analysis['fraud_alerts'].append({
                    "type": "🚨 PREDATORY INTEREST RATE",
                    "description": f"APR of {apr}% is extremely high",
                    "severity": "CRITICAL",
                    "action": "DO NOT SIGN. Report to authorities."
                })
                analysis['red_flags'].append(f"Predatory APR: {apr}%")
            elif apr > 18:
                analysis['fraud_alerts'].append({
                    "type": "⚠️ VERY HIGH INTEREST RATE",
                    "description": f"APR of {apr}% is above market",
                    "severity": "HIGH",
                    "action": "Negotiate aggressively."
                })
                analysis['yellow_flags'].append(f"High APR: {apr}%")
            elif apr_score >= 4:
                analysis['green_flags'].append(f"Good APR: {apr}%")
        
        # Fee analysis
        fee_keys = ['processing_fee', 'documentation_fee']
        total_fees = sum([contract_data.get(key, 0) for key in fee_keys])
        
        if total_fees > 1500:
            analysis['fraud_alerts'].append({
                "type": "💰 EXCESSIVE FEES",
                "description": f"Total fees of ${total_fees:,.2f} are high",
                "severity": "MEDIUM",
                "action": "Request fee reduction."
            })
            analysis['yellow_flags'].append("High fees detected")
        
        # Early termination
        if contract_data.get('has_early_termination', False):
            analysis['yellow_flags'].append("Early termination fees apply")
            analysis['recommendations'].append("Ask for specific early termination penalty amounts")
        
        # Calculate final score
        analysis['fairness_score'] = max(0, min(10, analysis['fairness_score']))
        
        # Determine risk level
        if len(analysis['fraud_alerts']) > 0 and any(a['severity'] == 'CRITICAL' for a in analysis['fraud_alerts']):
            analysis['risk_level'] = "Critical"
        elif analysis['fairness_score'] >= 8:
            analysis['risk_level'] = "Low"
        elif analysis['fairness_score'] >= 6:
            analysis['risk_level'] = "Medium"
        else:
            analysis['risk_level'] = "High"
        
        # Add recommendations
        if analysis['risk_level'] in ["High", "Critical"]:
            analysis['recommendations'].append("DO NOT SIGN without legal advice")
            analysis['recommendations'].append("Get competing offers")
        elif analysis['risk_level'] == "Medium":
            analysis['recommendations'].append("Negotiate better terms before signing")
        
        return analysis
    
    def _score_apr(self, apr):
        """Score APR from 1-5"""
        if apr <= 4.0: return 5
        elif apr <= 6.0: return 4
        elif apr <= 9.0: return 3
        elif apr <= 12.0: return 2
        else: return 1
    
    # ========== EMI CALCULATOR ==========
    
    def calculate_emi(self, principal, rate, tenure_months):
        """Calculate EMI"""
        monthly_rate = rate / 100 / 12
        if monthly_rate == 0:
            emi = principal / tenure_months
        else:
            emi = (principal * monthly_rate * (1 + monthly_rate) ** tenure_months) / \
                  ((1 + monthly_rate) ** tenure_months - 1)
        
        total_payable = emi * tenure_months
        total_interest = total_payable - principal
        
        return {
            "emi": round(emi, 2),
            "total_payable": round(total_payable, 2),
            "total_interest": round(total_interest, 2)
        }
    
    # ========== NEGOTIATION ASSISTANT ==========
    
    def get_negotiation_strategy(self, vehicle_info, dealer_price, context="india", language="english"):
        """Get negotiation strategy"""
        
        # Calculate target prices
        target_start = dealer_price * 0.80
        target_ideal = dealer_price * 0.85
        target_max = dealer_price * 0.90
        
        strategy = {
            "strategy": "Price-focused negotiation",
            "target_prices": {
                "start": round(target_start),
                "ideal": round(target_ideal),
                "maximum": round(target_max),
                "walk_away": round(dealer_price * 0.95)
            },
            "tactics": [],
            "scripts": {},
            "walk_away_points": []
        }
        
        if context == "india":
            strategy["tactics"] = [
                "Start with 15-20% below dealer price",
                "Mention competitors' offers",
                "Point out any minor defects",
                "Shop at month-end for sales targets",
                "Use cash payment as leverage"
            ]
            
            strategy["walk_away_points"] = [
                "APR above 12% with good credit",
                "Mandatory add-ons you don't want",
                "Pressure to sign immediately",
                "Fees exceeding ₹10,000",
                "No written commitment on trade-in value"
            ]
            
            # Tamil script - FIXED STRING
            tamil_script = '''**தமிழில் பேசுங்கள் (Speak confidently in Tamil):**

"சார், இந்த வாகனம் market-ல இப்போ ₹''' + f'{target_start:,}' + ''' க்கு கிடைக்குது. நான் இன்றைக்கே வாங்க ஆர்வமா இருக்கேன், ஆனால் இந்த price-ல முடியாது.

மற்ற showroom-ல ₹''' + f'{target_ideal:,}' + ''' quote குடுத்தாங்க. நீங்களும் இதே price-தான் குடுக்க முடியும்னா, நான் இப்பவே advance குடுத்து book பண்றேன்.

Free-ல ஏதாவது accessories குடுக்க முடியுமா? Floor mats, mud flaps, window tinting இதுல ஏதாவது ஒன்னு?"

**If they refuse:**
"சார், நான் வீட்ல போய் யோசிச்சிட்டு வரேன். இந்த price-ல நான் final ஆக்க முடியாது. நீங்க கூட வச்சுக்குங்க, நாளைக்கு பேசலாம்."'''
            
            strategy["scripts"]["tamil"] = tamil_script
            
        else:
            strategy["tactics"] = [
                "Start 20% below asking price",
                "Get competing quotes in writing",
                "Mention online market prices",
                "Negotiate fees separately",
                "Be ready to walk away"
            ]
            
            strategy["walk_away_points"] = [
                "APR above 8% with excellent credit",
                "Mandatory dealer add-ons",
                "Today-only pressure tactics",
                "Processing fees over $1,000",
                "VIN doesn't match vehicle"
            ]
        
        # English script
        english_script = f'''**Professional Approach:**

"I've done extensive research on this vehicle and comparable vehicles in the market. 
Based on current market conditions, I believe a fair price would be around ${target_ideal:,}.

I'm ready to proceed today if we can agree on a fair price. Here's what I'm looking for:
1. Final price: ${target_ideal:,}
2. All fees itemized and reasonable
3. Clean vehicle history report
4. Complete warranty documentation

What's the best out-the-door price you can offer?"'''
        
        strategy["scripts"]["english"] = english_script
        
        # Timing tips
        strategy["timing_tips"] = [
            "Shop at month-end when salespeople have quotas",
            "Visit on rainy days when showrooms are empty",
            "Avoid weekends when dealerships are busy",
            "December has year-end clearance sales",
            "End of financial quarter often has better deals"
        ]
        
        return strategy
    
    # ========== UNIVERSAL AI CHAT ASSISTANT ==========
    
    def chat_response(self, user_message, chat_history=None):
        """Universal ChatGPT-like assistant that can answer ANY question"""
        
        if chat_history is None:
            chat_history = []
        
        user_message_lower = user_message.lower()
        
        # Store context about the conversation
        context = self._analyze_conversation_context(chat_history, user_message)
        
        # Check if this is a follow-up question
        if self._is_follow_up_question(user_message, chat_history):
            return self._handle_follow_up(user_message, context, chat_history)
        
        # Detect language preference
        is_tamil = self._detect_tamil(user_message)
        
        # First, check if it's a car finance related question
        if self._is_car_finance_question(user_message_lower):
            return self._generate_car_finance_response(user_message, context, is_tamil)
        
        # If not car finance, use universal knowledge base
        return self._generate_universal_response(user_message, context, is_tamil)
    
    def _analyze_conversation_context(self, chat_history, current_message):
        """Analyze the conversation context"""
        context = {
            "topic": "general",
            "last_subject": None,
            "user_interests": [],
            "conversation_depth": 0,
            "is_technical": False
        }
        
        # Analyze last few messages
        recent_msgs = chat_history[-3:] if len(chat_history) > 3 else chat_history
        
        for msg in recent_msgs:
            if msg["role"] == "user":
                text = msg["content"].lower()
                
                # Detect technical terms
                tech_terms = ["python", "code", "algorithm", "api", "database", "server", "programming"]
                if any(term in text for term in tech_terms):
                    context["is_technical"] = True
                
                # Detect subject areas
                subjects = {
                    "technology": ["computer", "phone", "internet", "software", "app", "website"],
                    "finance": ["money", "investment", "stock", "bank", "loan", "interest"],
                    "education": ["study", "learn", "school", "college", "course", "exam"],
                    "health": ["health", "fitness", "diet", "exercise", "doctor", "medicine"],
                    "travel": ["travel", "trip", "vacation", "hotel", "flight", "destination"]
                }
                
                for subject, keywords in subjects.items():
                    if any(keyword in text for keyword in keywords):
                        context["last_subject"] = subject
                        context["user_interests"].append(subject)
                        break
        
        return context
    
    def _is_follow_up_question(self, user_message, chat_history):
        """Check if this is a follow-up question"""
        if len(chat_history) < 2:
            return False
        
        follow_up_indicators = [
            'and', 'also', 'what about', 'what if', 'how about',
            'can you explain', 'tell me more', 'elaborate',
            'idhu', 'andha', 'indha', 'ithu', 'athu',  # Tamil demonstratives
            'epdi', 'eppadi', 'enna', 'ethu'  # Tamil question words
        ]
        
        msg_lower = user_message.lower()
        return any(indicator in msg_lower for indicator in follow_up_indicators)
    
    def _detect_tamil(self, user_message):
        """Detect if user is writing in Tamil or Tanglish"""
        tamil_indicators = [
            'ah', 'ka', 'la', 'ta', 'vanga', 'sollunga', 'panlam',
            'enna', 'eppadi', 'idhu', 'andha', 'indha', 'ithu',
            'athu', 'ungal', 'ungaluku', 'ungalukku'
        ]
        
        msg_lower = user_message.lower()
        return any(indicator in msg_lower for indicator in tamil_indicators)
    
    def _is_car_finance_question(self, user_message_lower):
        """Check if question is about car finance"""
        car_keywords = [
            'car', 'vehicle', 'auto', 'automobile', 'vin',
            'price', 'cost', 'loan', 'emi', 'interest', 'apr',
            'finance', 'lease', 'buy', 'purchase', 'sell',
            'dealer', 'showroom', 'negotiate', 'bargain',
            'honda', 'toyota', 'ford', 'bmw', 'mercedes',
            'maruti', 'mahindra', 'tata', 'hyundai', 'suzuki',
            'கார்', 'வாகனம்', 'விலை', 'கடன்', 'வட்டி'  # Tamil car terms
        ]
        
        return any(keyword in user_message_lower for keyword in car_keywords)
    
    def _handle_follow_up(self, user_message, context, chat_history):
        """Handle follow-up questions intelligently"""
        
        if context.get("is_technical", False):
            return '''**Let me expand on that technical aspect:**

**Deeper Explanation:**
1. **Core Concept:** Breaking down the fundamental principles
2. **Practical Application:** How this applies in real-world scenarios
3. **Best Practices:** Industry standards and recommendations
4. **Common Pitfalls:** What to avoid and why
5. **Resources:** Where to learn more (documentation, tutorials, communities)

**Would you like me to:**
• Provide specific examples?
• Explain the implementation steps?
• Compare with alternative approaches?
• Show code snippets or pseudo-code?

**Just tell me what aspect you'd like me to elaborate on!**'''
        
        elif context.get("last_subject") == "finance":
            return '''**Let me provide more detailed financial insights:**

**Advanced Financial Analysis:**
1. **Risk Assessment:** Evaluating different risk factors
2. **Return Projections:** Potential outcomes and scenarios
3. **Market Trends:** Current economic indicators
4. **Regulatory Considerations:** Legal and compliance aspects
5. **Tax Implications:** How it affects your tax situation

**Specific areas I can elaborate:**
• Investment strategy optimization
• Risk management techniques
• Portfolio diversification
• Tax-efficient investing
• Market timing vs time in market

**What specific financial aspect interests you most?**'''
        
        elif context.get("last_subject") == "technology":
            return '''**Let me dive deeper into the technology aspects:**

**Technical Deep Dive:**
1. **Architecture:** System design and components
2. **Implementation:** How it's built and deployed
3. **Scalability:** Handling growth and load
4. **Security:** Protection mechanisms and best practices
5. **Maintenance:** Ongoing support and updates

**I can provide details on:**
• Specific technologies and frameworks
• Implementation code examples
• Performance optimization techniques
• Integration with other systems
• Future technology trends

**Which technical area would you like to explore further?**'''
        
        else:
            return '''**Let me provide more comprehensive information:**

**Expanded Discussion:**
1. **Historical Context:** Background and evolution
2. **Current State:** Present situation and trends
3. **Future Outlook:** Projections and predictions
4. **Global Perspective:** How this varies worldwide
5. **Personal Impact:** How this affects individuals

**I can elaborate on:**
• More examples and case studies
• Step-by-step guides
• Comparison with alternatives
• Pros and cons analysis
• Resource recommendations

**Tell me exactly what additional information would be helpful!**'''
    
    def _generate_car_finance_response(self, user_message, context, is_tamil):
        """Generate car finance specific responses"""
        
        if is_tamil:
            return self._generate_tamil_car_response(user_message)
        
        user_message_lower = user_message.lower()
        
        # VIN related questions
        if 'vin' in user_message_lower:
            return '''🔍 **VIN DECODING EXPERTISE**

I can decode any 17-character VIN worldwide! Here's what I provide:

**What I Analyze from VIN:**
1. **Manufacturer & Model** - Exact make and model
2. **Production Year** - When it was manufactured
3. **Factory Location** - Where it was built
4. **Vehicle Type** - Sedan, SUV, Truck, etc.
5. **Engine Specifications** - Engine type and size
6. **Safety Features** - Standard safety equipment
7. **Recall History** - Any manufacturer recalls

**For Any VIN:**
• Global brands (Toyota, Honda, BMW, Mercedes, etc.)
• Indian brands (Maruti, Mahindra, Tata, Hyundai, etc.)
• Electric vehicles (Tesla, BYD, MG, etc.)
• Commercial vehicles

**Just paste any VIN and I'll decode it instantly!**'''
        
        # Price related questions
        elif any(word in user_message_lower for word in ['price', 'cost', 'expensive', 'cheap', 'value']):
            return '''💰 **PRICE INTELLIGENCE SYSTEM**

I provide comprehensive price analysis for any vehicle:

**My Price Analysis Includes:**
1. **Market Benchmarking** - Current market rates
2. **Condition Assessment** - Based on mileage, age, condition
3. **Regional Variations** - Price differences by location
4. **Seasonal Factors** - Best/worst times to buy
5. **Negotiation Range** - What you should actually pay

**Price Categories I Analyze:**
• New cars (showroom prices)
• Used cars (private sellers & dealers)
• Certified Pre-Owned (CPO)
• Luxury & premium vehicles
• Electric & hybrid vehicles

**Tell me: Vehicle, Year, Asking Price, Condition - I'll tell you if it's fair!**'''
        
        # Loan/EMI questions
        elif any(word in user_message_lower for word in ['loan', 'emi', 'financing', 'interest', 'apr']):
            return '''🧮 **LOAN & EMI OPTIMIZATION ENGINE**

I calculate and optimize all loan parameters:

**What I Calculate:**
1. **EMI** - Exact monthly payment
2. **Total Interest** - Over entire loan term
3. **Best Tenure** - Optimal loan duration
4. **Down Payment** - Ideal initial payment
5. **Multiple Offers** - Compare different banks

**Loan Optimization Strategies:**
• Credit score impact on rates
• Balance transfer optimization
• Prepayment penalty analysis
• Fixed vs floating rate comparison
• Tax benefits calculation

**Share: Loan Amount, Interest Rate, Tenure - I'll optimize your EMI!**'''
        
        # Contract questions
        elif any(word in user_message_lower for word in ['contract', 'agreement', 'terms', 'clause']):
            return '''📄 **CONTRACT INTELLIGENCE & FRAUD DETECTION**

I analyze contracts for risks and unfair terms:

**What I Check:**
1. **Predatory Clauses** - Hidden fees and charges
2. **Interest Rate Analysis** - Fair vs excessive rates
3. **Termination Penalties** - Early exit costs
4. **Warranty Gaps** - What's not covered
5. **Legal Compliance** - Regulatory requirements

**Red Flags I Detect:**
• APR above 18% with good credit
• Processing fees over $1000
• Mandatory add-on packages
• Blank spaces in contract
• Pressure tactics documentation

**Paste any contract text - I'll analyze it line by line!**'''
        
        # Negotiation questions
        elif any(word in user_message_lower for word in ['negotiate', 'bargain', 'deal', 'discount']):
            return '''🤝 **NEGOTIATION INTELLIGENCE SYSTEM**

I provide exact negotiation strategies and scripts:

**My Negotiation Framework:**
1. **Preparation Phase** - Research and benchmarks
2. **Opening Strategy** - Initial offer positioning
3. **Counter Tactics** - Handling dealer responses
4. **Closing Techniques** - Final agreement strategies
5. **Walk Away Points** - When to exit negotiation

**Specific Scripts For:**
• New car purchases
• Used car negotiations
• Trade-in value maximization
• Dealer add-on avoidance
• Financing rate reduction

**Share dealer price and vehicle - I'll give you exact negotiation script!**'''
        
        # General car finance
        else:
            return '''🚗 **COMPREHENSIVE CAR FINANCE EXPERT**

I'm your all-in-one car finance intelligence system:

**Core Capabilities:**
🔍 **VIN Decoding** - Any vehicle worldwide
💰 **Price Intelligence** - Fair market value analysis
🧮 **EMI Optimization** - Loan calculation & comparison
📄 **Contract Review** - Fraud detection & risk assessment
🤝 **Negotiation AI** - Exact scripts & strategies
⚖️ **Offer Comparison** - Multiple deal analysis

**Ask me anything about:**
• Is this car price fair?
• How to get the best loan rate?
• What to check before buying?
• How to negotiate effectively?
• Which car is best for my budget?

**I provide detailed, step-by-step guidance for every car finance decision!**'''
    
    def _generate_tamil_car_response(self, user_message):
        """Generate Tamil responses for car finance questions"""
        
        user_message_lower = user_message.lower()
        
        if any(word in user_message_lower for word in ['price', 'vila', 'cost']):
            return '''**சார், விலை சரிபார்ப்புக்கு:**

**நான் சரிபார்க்கிறவை:**
1. **Market price** - இதே மாதிரி கார்கள் எவ்வளவு?
2. **Condition analysis** - mileage, accidents, service history
3. **Location factor** - உங்கள் பகுதிக்கு ஏற்ற விலை
4. **Negotiation range** - எவ்வளவு குறைக்க முடியும்?

**தகவல்கள் கொடுங்க:**
• கார் மாதிரி (எ.கா: Honda City)
• வருடம் (2020, 2021, etc.)
• கேட்கும் விலை
• நிலை (புதிய/பழைய)

**நான் சரியான விலை சொல்லித் தர்றேன்!**'''
        
        elif any(word in user_message_lower for word in ['loan', 'கடன்', 'emi']):
            return '''**கடன் விவரத்திற்கு:**

**நான் calculate பண்றது:**
1. **EMI** - மாதத்திற்கு எவ்வளவு?
2. **Total interest** - மொத்த வட்டி எவ்வளவு?
3. **Best banks** - எந்த bank குறைந்த வட்டி?
4. **Documents** - என்ன documents தேவை?

**தேவையான தகவல்கள்:**
• கடன் தொகை
• வட்டி விகிதம்
• கால அளவு (வருடங்கள்)
• உங்கள் credit score

**நான் best EMI plan சொல்லித் தர்றேன்!**'''
        
        else:
            return '''**கார் வாங்குறதுல expert advice வேணுமா?**

**நான் உதவுற விஷயங்கள்:**
🔍 **VIN decoding** - எந்த காரானாலும் சரி
💰 **விலை check** - fair price-ஆ சொல்றேன்
🧮 **EMI calculation** - loan details calculate
📄 **Contract review** - fraud check பண்றேன்
🤝 **Negotiation tips** - dealer-உட பேசுறது எப்படி?

**கேளுங்க:**
• "இந்த price correct ah?"
• "EMI எவ்வளவு வரும்?"
• "இந்த contract-ல problem உண்டா?"
• "Dealer-உட எப்படி negotiate பண்ணுவது?"

**நான் தமிழ்லயே clear-ஆ பதில் சொல்றேன்!**'''
    
    def _generate_universal_response(self, user_message, context, is_tamil):
        """Generate universal ChatGPT-like responses for ANY question"""
        
        if is_tamil:
            return self._generate_universal_tamil_response(user_message)
        
        user_message_lower = user_message.lower()
        
        # === CATEGORY DETECTION ===
        
        # Technology questions
        if any(word in user_message_lower for word in [
            'python', 'programming', 'code', 'software', 'app', 'website',
            'computer', 'tech', 'technology', 'algorithm', 'api', 'database'
        ]):
            return self._generate_tech_response(user_message)
        
        # Finance/Investment questions
        elif any(word in user_message_lower for word in [
            'invest', 'stock', 'mutual fund', 'bitcoin', 'crypto', 'trading',
            'saving', 'retirement', 'wealth', 'portfolio', 'market'
        ]):
            return self._generate_finance_response(user_message)
        
        # Education/Learning questions
        elif any(word in user_message_lower for word in [
            'learn', 'study', 'course', 'education', 'skill', 'certification',
            'online', 'university', 'college', 'exam', 'homework', 'assignment'
        ]):
            return self._generate_education_response(user_message)
        
        # Health/Fitness questions
        elif any(word in user_message_lower for word in [
            'health', 'fitness', 'exercise', 'diet', 'weight', 'gym',
            'yoga', 'meditation', 'nutrition', 'vitamin', 'doctor'
        ]):
            return self._generate_health_response(user_message)
        
        # Travel questions
        elif any(word in user_message_lower for word in [
            'travel', 'trip', 'vacation', 'hotel', 'flight', 'booking',
            'destination', 'tour', 'visa', 'passport', 'tourist'
        ]):
            return self._generate_travel_response(user_message)
        
        # Business questions
        elif any(word in user_message_lower for word in [
            'business', 'startup', 'entrepreneur', 'marketing', 'sales',
            'management', 'strategy', 'product', 'service', 'customer'
        ]):
            return self._generate_business_response(user_message)
        
        # Personal development
        elif any(word in user_message_lower for word in [
            'motivation', 'goal', 'success', 'productivity', 'time management',
            'happiness', 'mindset', 'confidence', 'leadership', 'communication'
        ]):
            return self._generate_personal_dev_response(user_message)
        
        # Science questions
        elif any(word in user_message_lower for word in [
            'science', 'physics', 'chemistry', 'biology', 'math', 'mathematics',
            'engineering', 'research', 'experiment', 'theory', 'discovery'
        ]):
            return self._generate_science_response(user_message)
        
        # Current affairs
        elif any(word in user_message_lower for word in [
            'news', 'current', 'politics', 'government', 'economy', 'world',
            'update', 'trending', 'viral', 'social media', 'latest'
        ]):
            return self._generate_current_affairs_response(user_message)
        
        # Creative/Arts
        elif any(word in user_message_lower for word in [
            'art', 'music', 'writing', 'design', 'creative', 'painting',
            'photography', 'film', 'movie', 'literature', 'poetry'
        ]):
            return self._generate_creative_response(user_message)
        
        # General knowledge
        else:
            return self._generate_general_knowledge_response(user_message)
    
    def _generate_universal_tamil_response(self, user_message):
        """Generate universal Tamil responses"""
        
        return '''**உங்கள் கேள்விக்கு தமிழில் பதில்!**

நான் ஒரு முழுமையான AI உதவியாளன். எந்த விஷயத்தையும் பற்றி கேளுங்கள்:

**நான் உதவும் துறைகள்:**
💻 **தொழில்நுட்பம்** - கம்ப்யூட்டர், மொபைல், இன்டர்நெட்
💰 **நிதி** - முதலீடு, சேமிப்பு, வங்கி
📚 **கல்வி** - படிப்பு, பாடம், வேலைவாய்ப்பு
🏥 **ஆரோக்கியம்** - உடல் நலம், உணவு, வயிற்றுப் பயிற்சி
✈️ **பயணம்** - ஹோட்டல், டிக்கட், இடங்கள்
💼 **வியாபாரம்** - தொழில், விற்பனை, மார்க்கெட்டிங்
🧠 **தனிப்பட்ட வளர்ச்சி** - உற்சாகம், இலக்கு, நேர மேலாண்மை

**எடுத்துக்காட்டு கேள்விகள்:**
• "Python programming எப்படி கற்றுக்கொள்வது?"
• "Stock market-ல எப்படி முதலீடு செய்வது?"
• "Healthy diet plan என்ன?"
• "Business start செய்ய tips என்ன?"
• "Time management எப்படி செய்வது?"

**எந்த கேள்வியும் கேளுங்கள் - நான் விரிவாக விளக்குவேன்!**'''
    
    def _generate_tech_response(self, user_message):
        """Generate technology related responses"""
        
        return f'''**🧠 TECHNOLOGY INTELLIGENCE RESPONSE**

I understand you're asking about technology. Let me provide comprehensive insights:

**Technology Analysis Framework:**

1. **Fundamental Concepts**
   • Core principles and theories
   • Historical development context
   • Current industry standards
   • Future trends and predictions

2. **Practical Implementation**
   • Step-by-step implementation guide
   • Best practices and patterns
   • Common challenges and solutions
   • Performance optimization tips

3. **Learning Pathway**
   • Prerequisites and foundation skills
   • Recommended learning resources
   • Practice projects and exercises
   • Certification and career paths

4. **Industry Applications**
   • Real-world use cases
   • Business value and ROI
   • Integration with other technologies
   • Scalability and maintenance considerations

**Based on your question, I can provide specific guidance on:**
• Programming languages and frameworks
• Software development methodologies
• System architecture and design
• Data management and analytics
• Cybersecurity and best practices
• Emerging technologies (AI, Blockchain, IoT)

**Would you like me to elaborate on any specific aspect of technology?**'''
    
    def _generate_finance_response(self, user_message):
        """Generate finance/investment responses"""
        
        return f'''**💰 FINANCIAL INTELLIGENCE RESPONSE**

I understand you're asking about finance/investments. Here's my analytical framework:

**Financial Analysis Structure:**

1. **Investment Principles**
   • Risk vs reward assessment
   • Diversification strategies
   • Time horizon considerations
   • Liquidity requirements

2. **Market Analysis**
   • Economic indicators review
   • Sector performance trends
   • Regulatory environment
   • Global market correlations

3. **Portfolio Strategy**
   • Asset allocation models
   • Rebalancing techniques
   • Tax-efficient investing
   • Retirement planning

4. **Risk Management**
   • Risk tolerance assessment
   • Hedging strategies
   • Insurance integration
   • Emergency fund planning

**Specific Areas I Can Discuss:**
• Stock market investing strategies
• Mutual fund selection criteria
• Real estate investment analysis
• Retirement planning optimization
• Tax planning and efficiency
• Cryptocurrency and digital assets

**What specific financial topic would you like to explore?**'''
    
    def _generate_education_response(self, user_message):
        """Generate education/learning responses"""
        
        return f'''**📚 EDUCATION INTELLIGENCE RESPONSE**

I understand you're asking about learning/education. Here's my learning framework:

**Education Strategy Framework:**

1. **Learning Objectives**
   • Skill gap analysis
   • Goal setting methodology
   • Success metrics definition
   • Timeline planning

2. **Learning Methods**
   • Self-paced online learning
   • Structured courses and programs
   • Practical project-based learning
   • Mentorship and coaching

3. **Resource Optimization**
   • Free vs paid resources
   • Time management techniques
   • Study habit optimization
   • Learning environment setup

4. **Assessment & Progress**
   • Knowledge retention techniques
   • Practical application strategies
   • Certification preparation
   • Career transition planning

**I Can Guide You On:**
• Career-specific learning paths
• Online course selection criteria
• Study techniques and memory improvement
• Exam preparation strategies
• Skill certification processes
• Continuing education opportunities

**What specific learning goal would you like to achieve?**'''
    
    def _generate_health_response(self, user_message):
        """Generate health/fitness responses"""
        
        return f'''**🏥 HEALTH & FITNESS INTELLIGENCE RESPONSE**

I understand you're asking about health/fitness. Here's my wellness framework:

**Health & Wellness Framework:**

1. **Nutrition Strategy**
   • Balanced diet planning
   • Macronutrient optimization
   • Micronutrient requirements
   • Hydration and timing

2. **Exercise Planning**
   • Cardiovascular fitness
   • Strength training programs
   • Flexibility and mobility
   • Recovery and rest periods

3. **Lifestyle Factors**
   • Sleep optimization techniques
   • Stress management strategies
   • Habit formation psychology
   • Environmental wellness

4. **Medical Considerations**
   • Preventive health measures
   • Regular check-up schedules
   • Warning signs awareness
   • Professional consultation guidance

**I Can Provide Guidance On:**
• Weight management strategies
• Fitness program customization
• Healthy eating habits
• Mental wellness techniques
• Chronic condition management
• Preventive healthcare measures

**What specific health or fitness goal are you working towards?**'''
    
    def _generate_travel_response(self, user_message):
        """Generate travel related responses"""
        
        return f'''**✈️ TRAVEL INTELLIGENCE RESPONSE**

I understand you're asking about travel. Here's my travel planning framework:

**Travel Planning Framework:**

1. **Destination Research**
   • Climate and seasonal considerations
   • Cultural norms and etiquette
   • Safety and security assessment
   • Local attractions and activities

2. **Logistics Planning**
   • Transportation options comparison
   • Accommodation selection criteria
   • Budget allocation strategies
   • Timeline and itinerary optimization

3. **Preparation Checklist**
   • Documentation requirements
   • Packing optimization tips
   • Health and vaccination needs
   • Travel insurance selection

4. **Experience Optimization**
   • Local cuisine exploration
   • Cultural immersion strategies
   • Photography and memory creation
   • Sustainable travel practices

**I Can Help With:**
• International travel planning
• Budget travel strategies
• Luxury travel experiences
• Family vacation planning
• Solo travel safety tips
• Adventure travel preparation

**What type of travel experience are you planning?**'''
    
    def _generate_business_response(self, user_message):
        """Generate business/startup responses"""
        
        return f'''**💼 BUSINESS INTELLIGENCE RESPONSE**

I understand you're asking about business/entrepreneurship. Here's my business framework:

**Business Strategy Framework:**

1. **Market Analysis**
   • Target audience identification
   • Competitor analysis methodology
   • Market gap identification
   • Trend analysis and forecasting

2. **Business Model Design**
   • Revenue stream development
   • Cost structure optimization
   • Value proposition creation
   • Customer acquisition strategy

3. **Operations Planning**
   • Team building and management
   • Process optimization techniques
   • Technology integration strategy
   • Scalability planning

4. **Growth Strategy**
   • Marketing channel optimization
   • Sales funnel development
   • Partnership and collaboration
   • Funding and investment strategy

**I Can Provide Guidance On:**
• Startup launch checklist
• Business plan development
• Marketing strategy creation
• Financial management
• Team leadership
• Scaling operations

**What specific business challenge are you facing?**'''
    
    def _generate_personal_dev_response(self, user_message):
        """Generate personal development responses"""
        
        return f'''**🧠 PERSONAL DEVELOPMENT INTELLIGENCE RESPONSE**

I understand you're asking about personal growth. Here's my development framework:

**Personal Development Framework:**

1. **Self-Assessment**
   • Strengths and weaknesses analysis
   • Values and purpose identification
   • Goal setting methodology
   • Progress tracking systems

2. **Skill Development**
   • Learning strategy optimization
   • Habit formation techniques
   • Time management systems
   • Productivity enhancement methods

3. **Mindset Cultivation**
   • Growth mindset development
   • Emotional intelligence building
   • Resilience and adaptability
   • Confidence and self-esteem

4. **Relationship Building**
   • Communication skill enhancement
   • Networking strategies
   • Conflict resolution techniques
   • Leadership development

**I Can Guide You On:**
• Career advancement strategies
• Life balance optimization
• Stress management techniques
• Decision-making improvement
• Motivation maintenance
• Purpose and meaning discovery

**What area of personal development would you like to focus on?**'''
    
    def _generate_science_response(self, user_message):
        """Generate science related responses"""
        
        return f'''**🔬 SCIENCE INTELLIGENCE RESPONSE**

I understand you're asking about science. Here's my scientific analysis framework:

**Scientific Analysis Framework:**

1. **Fundamental Principles**
   • Core theories and laws
   • Historical development context
   • Current scientific consensus
   • Open questions and mysteries

2. **Methodology & Process**
   • Scientific method application
   • Experimental design principles
   • Data analysis techniques
   • Peer review and validation

3. **Practical Applications**
   • Technology development
   • Medical and health applications
   • Environmental implications
   • Daily life relevance

4. **Future Directions**
   • Emerging research areas
   • Technological breakthroughs
   • Ethical considerations
   • Global collaboration needs

**I Can Discuss:**
• Physics and cosmology
• Chemistry and materials science
• Biology and genetics
• Mathematics and statistics
• Engineering principles
• Environmental science

**What specific scientific topic interests you?**'''
    
    def _generate_current_affairs_response(self, user_message):
        """Generate current affairs responses"""
        
        return f'''**📰 CURRENT AFFAIRS INTELLIGENCE RESPONSE**

I understand you're asking about current events. Here's my analysis framework:

**Current Affairs Analysis Framework:**

1. **Event Contextualization**
   • Historical background analysis
   • Geographic and cultural context
   • Key stakeholders identification
   • Timeline of developments

2. **Impact Assessment**
   • Economic implications
   • Social and cultural effects
   • Political consequences
   • Global relations impact

3. **Multiple Perspectives**
   • Different stakeholder viewpoints
   • Media coverage analysis
   • Expert opinions and analysis
   • Public sentiment assessment

4. **Future Implications**
   • Short-term consequences
   • Long-term trends
   • Policy change possibilities
   • Global implications

**I Can Provide Analysis On:**
• Political developments
• Economic trends and indicators
• Social movements and changes
• Technological advancements
• Environmental issues
• International relations

**What current event would you like to understand better?**'''
    
    def _generate_creative_response(self, user_message):
        """Generate creative/arts responses"""
        
        return f'''**🎨 CREATIVE INTELLIGENCE RESPONSE**

I understand you're asking about creative/arts. Here's my creative framework:

**Creative Process Framework:**

1. **Inspiration & Ideation**
   • Creative stimulus sources
   • Idea generation techniques
   • Brainstorming methodologies
   • Theme and concept development

2. **Skill Development**
   • Technical skill building
   • Artistic style development
   • Tool and medium mastery
   • Practice and refinement techniques

3. **Creative Execution**
   • Project planning and management
   • Workflow optimization
   • Quality control methods
   • Completion and presentation

4. **Creative Business**
   • Portfolio development
   • Marketing and promotion
   • Client acquisition strategies
   • Pricing and valuation

**I Can Guide You On:**
• Visual arts and design
• Writing and literature
• Music composition and production
• Photography and filmmaking
• Performing arts
• Creative entrepreneurship

**What creative pursuit would you like to explore?**'''
    
    def _generate_general_knowledge_response(self, user_message):
        """Generate general knowledge responses"""
        
        return f'''**🌐 UNIVERSAL KNOWLEDGE RESPONSE**

I understand you're asking a general question. Here's my comprehensive approach:

**Knowledge Analysis Framework:**

1. **Context Establishment**
   • Topic definition and scope
   • Historical background
   • Current relevance
   • Global perspectives

2. **Information Synthesis**
   • Multiple source integration
   • Fact verification methodology
   • Expert consensus identification
   • Contradictory information resolution

3. **Practical Application**
   • Real-world implications
   • Personal relevance assessment
   • Decision-making guidance
   • Actionable next steps

4. **Further Exploration**
   • Recommended resources
   • Learning pathways
   • Expert consultation guidance
   • Community engagement options

**I Can Help You Understand:**
• Complex concepts simplified
• Historical events and significance
• Cultural practices and traditions
• Scientific phenomena explained
• Philosophical ideas and theories
• Practical life skills and knowledge

**Feel free to ask about ANY topic - I'll provide detailed, well-researched insights!**

💡 **Tip:** You can ask me about anything from quantum physics to cooking recipes, from stock markets to meditation techniques, from programming to relationship advice!'''

# ========== STREAMLIT UI ==========

assistant = CarFinanceAssistant()

def main():
    # Sidebar for navigation
    st.sidebar.title("🚗 Car Finance Assistant")
    st.sidebar.markdown("---")
    
    menu_options = [
        "💬 Universal AI Assistant",
        "🔍 VIN Decoder", 
        "💰 Price Check",
        "🧮 EMI Calculator",
        "📄 Contract Review",
        "🤝 Negotiation Help",
        "⚖️ Compare Offers"
    ]
    
    selected_menu = st.sidebar.selectbox("Choose Feature", menu_options)
    
    st.sidebar.markdown("---")
    st.sidebar.info('''
    **💡 Quick Tips:**
    • Always check VIN before buying
    • Compare 3+ loan offers
    • Negotiate price before financing
    • Read full contract carefully
    • Walk away from pressure tactics
    ''')
    
    # Main content
    st.title("🚗 Car Finance AI Assistant")
    st.markdown("### Your Expert Advisor for Smart Car Financing Decisions")
    
    if selected_menu == "💬 Universal AI Assistant":
        render_chat_assistant()
    
    elif selected_menu == "🔍 VIN Decoder":
        render_vin_decoder()
    
    elif selected_menu == "💰 Price Check":
        render_price_check()
    
    elif selected_menu == "🧮 EMI Calculator":
        render_emi_calculator()
    
    elif selected_menu == "📄 Contract Review":
        render_contract_review()
    
    elif selected_menu == "🤝 Negotiation Help":
        render_negotiation_help()
    
    elif selected_menu == "⚖️ Compare Offers":
        render_compare_offers()

def render_chat_assistant():
    st.header("💬 Universal AI Assistant")
    st.markdown("""
    **ChatGPT-like intelligence that can answer ANY question!**
    
    *Ask me about cars, technology, finance, health, travel, science, or anything else!*
    *தமிழிலும் கேளுங்கள் - நான் தமிழிலும் பதிலளிப்பேன்!*
    """)
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": """🤖 **UNIVERSAL AI ASSISTANT READY!**

I'm your all-purpose AI assistant with ChatGPT-level intelligence. I can help you with **ANY topic**:

**🌐 CATEGORIES I COVER:**
• **Technology** - Programming, AI, Software, Hardware
• **Finance** - Investments, Stocks, Loans, Budgeting
• **Education** - Learning, Courses, Skills, Careers
• **Health** - Fitness, Nutrition, Wellness, Medicine
• **Travel** - Planning, Destinations, Booking, Tips
• **Business** - Startups, Marketing, Management, Strategy
• **Science** - Physics, Biology, Chemistry, Research
• **Personal Development** - Motivation, Goals, Productivity
• **Creative Arts** - Writing, Music, Design, Photography
• **Car Finance** - VIN, Pricing, Loans, Contracts

**💬 ASK ME ANYTHING:**
• "How to learn Python programming?"
• "What's the best investment strategy?"
• "How to start a successful business?"
• "Tips for healthy lifestyle?"
• "Travel planning guide for Europe?"
• "Is this car price fair?"

**தமிழ்லயும் கேளுங்கள் - எந்த கேள்வியும் கேளுங்கள்!**"""}
        ]
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything...", key="chat_input"):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking deeply..."):
                response = assistant.chat_response(prompt, st.session_state.chat_history)
                st.markdown(response)
        
        # Add AI response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Quick action buttons
    st.markdown("---")
    st.subheader("💡 Quick Topics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    quick_topics = [
        ("💻 Tech Help", "How to learn programming?"),
        ("💰 Finance", "Best investment strategy?"),
        ("📚 Education", "How to study effectively?"),
        ("🏥 Health", "Tips for healthy lifestyle?")
    ]
    
    for i, (btn_text, question) in enumerate(quick_topics):
        with [col1, col2, col3, col4][i]:
            if st.button(btn_text, use_container_width=True, key=f"topic_{i}"):
                st.session_state.chat_history.append({"role": "user", "content": question})
                st.rerun()
    
    # Conversation management
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New Conversation", use_container_width=True, type="secondary"):
            st.session_state.chat_history = [
                {"role": "assistant", "content": "Conversation refreshed! Ask me anything - I can help with any topic!"}
            ]
            st.rerun()
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True, type="secondary"):
            st.session_state.chat_history = [
                {"role": "assistant", "content": "Chat cleared! I'm ready to help with any questions you have."}
            ]
            st.rerun()

def render_vin_decoder():
    st.header("🔍 VIN Decoder")
    st.markdown("Enter any 17-character VIN to decode vehicle information")
    
    vin = st.text_input("Vehicle Identification Number (VIN)", 
                       placeholder="Example: 1HGCM82633A123456 or MA1PA24B8M1234567",
                       max_chars=17)
    
    col1, col2 = st.columns(2)
    with col1:
        currency = st.selectbox("Currency", ["USD", "INR"])
    with col2:
        country = st.selectbox("Location", ["USA", "India", "Global"])
    
    if st.button("🚗 Decode VIN", type="primary"):
        if len(vin) == 17:
            with st.spinner("Decoding VIN..."):
                result = assistant.decode_vin(vin)
                st.session_state.current_vin = vin
                
                st.markdown("---")
                st.success("✅ Vehicle Information Found")
                
                # Display info
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Manufacturer", result.get('manufacturer', 'Unknown'))
                with col2:
                    st.metric("Model", result.get('model', 'Unknown'))
                with col3:
                    st.metric("Year", result.get('year', 'Unknown'))
                
                # Details
                st.subheader("📋 Vehicle Details")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Country:** {result.get('country', 'Unknown')}")
                    st.write(f"**Engine:** {result.get('engine', 'Unknown')}")
                    st.write(f"**Fuel Type:** {result.get('fuel_type', 'Unknown')}")
                with col2:
                    st.write(f"**Transmission:** {result.get('transmission', 'Unknown')}")
                    st.write(f"**Segment:** {result.get('segment', 'Unknown')}")
                    st.write(f"**Safety:** {result.get('safety_rating', 'Unknown')}")
                
                # Price check option
                if result.get('msrp'):
                    st.subheader("💰 Price Check")
                    symbol = "$" if currency == "USD" else "₹"
                    asking_price = st.number_input(f"Your Asking Price ({symbol})", 
                                                  value=int(result['msrp']),
                                                  step=1000 if currency == "USD" else 50000)
                    
                    if st.button("Check Price Fairness"):
                        vehicle_info = {
                            **result,
                            'condition': 'good',
                            'mileage': 0
                        }
                        price_analysis = assistant.analyze_price(vehicle_info, asking_price, currency)
                        
                        st.markdown(f"### {price_analysis['fairness']}")
                        st.info(f"**Recommendation:** {price_analysis['recommendation']}")
                        
                        details = price_analysis['details']
                        st.write(f"• Market Price: {details['symbol']}{details['market_price']:,}")
                        st.write(f"• Your Price: {details['symbol']}{details['asking_price']:,}")
                        st.write(f"• Difference: {details['symbol']}{abs(details['difference']):,} ({details['percentage_difference']}%)")
        else:
            st.error("Please enter a valid 17-character VIN")

def render_price_check():
    st.header("💰 Price Check")
    st.markdown("Check if a vehicle price is fair compared to market rates")
    
    with st.form("price_check_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            manufacturer = st.text_input("Manufacturer*", "Toyota")
            model = st.text_input("Model*", "Camry")
            year = st.number_input("Year*", 2010, 2024, 2022)
            asking_price = st.number_input("Asking Price*", 1000, 500000, 25000, 1000)
            currency = st.selectbox("Currency*", ["USD", "INR"])
        
        with col2:
            condition = st.selectbox("Condition*", ["Excellent", "Good", "Fair", "Poor"])
            mileage = st.number_input("Mileage", 0, 300000, 15000, 1000)
            vehicle_type = st.selectbox("Type", ["New", "Used", "CPO"])
        
        submitted = st.form_submit_button("🔍 Check Price", type="primary")
    
    if submitted:
        vehicle_info = {
            "manufacturer": manufacturer,
            "model": model,
            "year": year,
            "condition": condition,
            "mileage": mileage,
            "type": vehicle_type,
            "msrp": 25000 if currency == "USD" else 1500000
        }
        
        with st.spinner("Analyzing market price..."):
            analysis = assistant.analyze_price(vehicle_info, asking_price, currency)
            
            st.markdown("---")
            st.header("📊 Price Analysis")
            
            # Results
            col1, col2, col3 = st.columns(3)
            symbol = "$" if currency == "USD" else "₹"
            
            with col1:
                st.markdown(f"### {analysis['fairness']}")
            with col2:
                st.metric("Asking Price", f"{symbol}{asking_price:,}")
            with col3:
                st.metric("Fair Price", f"{symbol}{analysis['details']['adjusted_price']:,}")
            
            # Details
            st.info(f"**Recommendation:** {analysis['recommendation']}")
            
            details = analysis['details']
            st.write(f"**Market Reference:** {symbol}{details['market_price']:,}")
            st.write(f"**Condition Adjusted:** {symbol}{details['adjusted_price']:,}")
            st.write(f"**Difference:** {symbol}{abs(details['difference']):,} ({details['percentage_difference']}%)")
            
            # Negotiation tips
            if details['difference'] > 0:
                st.subheader("🎯 Negotiation Strategy")
                st.write("**Target Price Range:**")
                st.write(f"• Start at: {symbol}{int(asking_price * 0.8):,}")
                st.write(f"• Target: {symbol}{int(asking_price * 0.85):,}")
                st.write(f"• Maximum: {symbol}{int(asking_price * 0.9):,}")

def render_emi_calculator():
    st.header("🧮 EMI Calculator")
    st.markdown("Calculate EMI and compare loan offers")
    
    tab1, tab2 = st.tabs(["EMI Calculator", "Compare Loans"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            loan_amount = st.number_input("Loan Amount", 10000, 1000000, 25000, 1000)
            interest_rate = st.slider("Interest Rate (%)", 2.0, 20.0, 5.5, 0.1)
        
        with col2:
            tenure_years = st.slider("Loan Tenure (Years)", 1, 7, 5)
            tenure_months = tenure_years * 12
        
        if st.button("Calculate EMI", type="primary"):
            emi_result = assistant.calculate_emi(loan_amount, interest_rate, tenure_months)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Monthly EMI", f"${emi_result['emi']:,.0f}")
            with col2:
                st.metric("Total Payable", f"${emi_result['total_payable']:,.0f}")
            with col3:
                st.metric("Total Interest", f"${emi_result['total_interest']:,.0f}")
            
            # Breakdown
            st.subheader("📊 Loan Breakdown")
            df = pd.DataFrame({
                'Year': list(range(1, tenure_years + 1)),
                'Principal': [loan_amount/tenure_years] * tenure_years,
                'Interest': [emi_result['total_interest']/tenure_years] * tenure_years,
                'Balance': [loan_amount - (i * loan_amount/tenure_years) for i in range(tenure_years)]
            })
            st.dataframe(df.style.format("{:,.0f}"), use_container_width=True)
    
    with tab2:
        st.subheader("Compare Loan Offers")
        
        num_offers = st.number_input("Number of offers", 2, 5, 3)
        offers = []
        
        for i in range(num_offers):
            with st.expander(f"Offer {i+1}", expanded=i==0):
                col1, col2 = st.columns(2)
                with col1:
                    bank = st.text_input(f"Bank", f"Bank {i+1}", key=f"bank_{i}")
                    principal = st.number_input(f"Amount", 10000, 1000000, 25000, 1000, key=f"amt_{i}")
                    rate = st.number_input(f"Rate %", 2.0, 20.0, 5.5 + i, 0.1, key=f"rate_{i}")
                with col2:
                    tenure = st.number_input(f"Months", 12, 84, 60, 6, key=f"ten_{i}")
                    fee = st.number_input(f"Fee", 0, 5000, 500, 50, key=f"fee_{i}")
                
                emi = assistant.calculate_emi(principal, rate, tenure)
                offers.append({
                    'bank': bank,
                    'emi': emi['emi'],
                    'total': emi['total_payable'],
                    'rate': rate,
                    'fee': fee
                })
        
        if st.button("Compare", type="primary"):
            # Create comparison table
            comp_data = []
            for offer in offers:
                comp_data.append({
                    'Bank': offer['bank'],
                    'Rate': f"{offer['rate']}%",
                    'EMI': f"${offer['emi']:,.0f}",
                    'Total': f"${offer['total']:,.0f}",
                    'Fee': f"${offer['fee']:,.0f}"
                })
            
            # Sort by total cost
            comp_data.sort(key=lambda x: float(x['Total'].replace('$', '').replace(',', '')))
            
            st.subheader("🏆 Best Offer")
            best = comp_data[0]
            st.success(f"**{best['Bank']}** - EMI: {best['EMI']}")
            
            st.subheader("📊 Comparison")
            st.dataframe(pd.DataFrame(comp_data), use_container_width=True)

def render_contract_review():
    st.header("📄 Contract Review")
    st.markdown("Analyze car loan/lease contracts for unfair terms")
    
    input_method = st.radio("Input Method:", ["Paste Text", "Sample"], horizontal=True)
    
    contract_text = ""
    
    if input_method == "Sample":
        sample = '''CAR LOAN AGREEMENT

Loan Amount: $25,000
APR: 12.5%
Term: 60 months
Monthly Payment: $562.50
Total Amount: $33,750
Down Payment: $3,000
Processing Fee: $500
Documentation Fee: $250

Terms:
- Early termination fee applies
- Late payment penalty: $50
- Insurance mandatory'''
        contract_text = st.text_area("Sample Contract:", sample, height=200)
    else:
        contract_text = st.text_area("Paste Contract Text:", height=200)
    
    if st.button("🔍 Analyze Contract", type="primary") and contract_text:
        with st.spinner("Analyzing..."):
            contract_data = assistant.extract_contract_data(contract_text)
            analysis = assistant.analyze_contract_complete(contract_data)
            
            st.markdown("---")
            
            # Score
            col1, col2, col3 = st.columns(3)
            with col1:
                score = analysis['fairness_score']
                if score >= 8:
                    st.success(f"## ⭐⭐⭐⭐⭐\n### {score}/10")
                elif score >= 6:
                    st.warning(f"## ⭐⭐⭐⭐\n### {score}/10")
                elif score >= 4:
                    st.warning(f"## ⭐⭐⭐\n### {score}/10")
                else:
                    st.error(f"## ⭐⭐\n### {score}/10")
            
            with col2:
                risk = analysis['risk_level']
                if risk == "Low":
                    st.success(f"## 🟢\n### {risk}")
                elif risk == "Medium":
                    st.warning(f"## 🟡\n### {risk}")
                else:
                    st.error(f"## 🔴\n### {risk}")
            
            with col3:
                issues = len(analysis['red_flags']) + len(analysis['yellow_flags'])
                if issues == 0:
                    st.success(f"## ✅\n### {issues} Issues")
                elif issues <= 3:
                    st.warning(f"## ⚠️\n### {issues} Issues")
                else:
                    st.error(f"## 🚨\n### {issues} Issues")
            
            # Fraud alerts
            if analysis['fraud_alerts']:
                st.subheader("🚨 Fraud Alerts")
                for alert in analysis['fraud_alerts']:
                    with st.expander(f"{alert['type']}", expanded=True):
                        st.error(alert['description'])
                        st.info(f"**Action:** {alert['action']}")
            
            # Flags
            col1, col2 = st.columns(2)
            with col1:
                if analysis['red_flags']:
                    st.subheader("🔴 Red Flags")
                    for flag in analysis['red_flags']:
                        st.error(f"• {flag}")
            
            with col2:
                if analysis['yellow_flags']:
                    st.subheader("🟡 Yellow Flags")
                    for flag in analysis['yellow_flags']:
                        st.warning(f"• {flag}")
            
            # Recommendations
            if analysis['recommendations']:
                st.subheader("💡 Recommendations")
                for rec in analysis['recommendations']:
                    st.info(f"• {rec}")

def render_negotiation_help():
    st.header("🤝 Negotiation Help")
    st.markdown("Get personalized negotiation strategies")
    
    col1, col2 = st.columns(2)
    
    with col1:
        vehicle_type = st.selectbox("Vehicle Type", ["Sedan", "SUV", "Hatchback", "Luxury"])
        dealer_price = st.number_input("Dealer Price", 10000, 100000, 25000, 1000)
        currency = st.selectbox("Currency", ["USD", "INR"])
    
    with col2:
        location = st.selectbox("Location", ["Dealer", "Private Seller", "Online"])
        language = st.selectbox("Language", ["English", "Tamil"])
    
    if st.button("🎯 Get Strategy", type="primary"):
        vehicle_info = {"model": vehicle_type}
        strategy = assistant.get_negotiation_strategy(vehicle_info, dealer_price, 
                                                     "india" if currency == "INR" else "global",
                                                     language.lower())
        
        st.markdown("---")
        st.header("🎯 Negotiation Strategy")
        
        # Targets
        symbol = "$" if currency == "USD" else "₹"
        targets = strategy['target_prices']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Start Offer", f"{symbol}{targets['start']:,}")
        with col2:
            st.metric("Target Price", f"{symbol}{targets['ideal']:,}")
        with col3:
            st.metric("Max Price", f"{symbol}{targets['maximum']:,}")
        with col4:
            st.metric("Walk Away", f"{symbol}{targets['walk_away']:,}")
        
        # Tactics
        st.subheader("🎭 Tactics")
        for tactic in strategy['tactics']:
            st.write(f"• {tactic}")
        
        # Script
        st.subheader("📝 Script")
        script_key = "tamil" if language == "Tamil" else "english"
        if script_key in strategy['scripts']:
            st.markdown(strategy['scripts'][script_key])
        
        # Walk away points
        st.subheader("🚶 Walk Away If")
        for point in strategy['walk_away_points']:
            st.error(f"• {point}")

def render_compare_offers():
    st.header("⚖️ Compare Offers")
    st.markdown("Compare multiple vehicle offers")
    
    num_offers = st.number_input("Number of offers", 2, 5, 2)
    offers = []
    
    for i in range(num_offers):
        with st.expander(f"Offer {i+1}", expanded=i==0):
            col1, col2 = st.columns(2)
            with col1:
                dealer = st.text_input(f"Dealer", f"Dealer {i+1}", key=f"dlr_{i}")
                vehicle = st.text_input(f"Vehicle", "Honda Accord", key=f"veh_{i}")
                price = st.number_input(f"Price", 10000, 100000, 25000, 1000, key=f"prc_{i}")
            with col2:
                apr = st.number_input(f"APR %", 2.0, 20.0, 5.5, 0.1, key=f"apr_{i}")
                term = st.number_input(f"Term (months)", 12, 84, 60, 6, key=f"trm_{i}")
                down = st.number_input(f"Down Payment", 0, 50000, 3000, 500, key=f"dwn_{i}")
            
            emi = assistant.calculate_emi(price - down, apr, term)
            offers.append({
                'dealer': dealer,
                'vehicle': vehicle,
                'price': price,
                'apr': apr,
                'emi': emi['emi'],
                'total': emi['total_payable'] + down
            })
    
    if st.button("Compare Offers", type="primary"):
        # Create comparison
        comp_data = []
        for offer in offers:
            comp_data.append({
                'Dealer': offer['dealer'],
                'Vehicle': offer['vehicle'],
                'Price': f"${offer['price']:,}",
                'APR': f"{offer['apr']}%",
                'EMI': f"${offer['emi']:,.0f}",
                'Total': f"${offer['total']:,.0f}"
            })
        
        # Sort by total
        comp_data.sort(key=lambda x: float(x['Total'].replace('$', '').replace(',', '')))
        
        st.subheader("🏆 Best Offer")
        best = comp_data[0]
        st.success(f"**{best['Dealer']}** - Total: {best['Total']}")
        
        st.subheader("📊 Comparison Table")
        st.dataframe(pd.DataFrame(comp_data), use_container_width=True)

if __name__ == "__main__":
    main()