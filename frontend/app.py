import streamlit as st
import pandas as pd
import numpy as np
import json
import re
from datetime import datetime
import base64
import io

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="Car Lease AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== AI THEME BACKGROUND ==========
st.markdown("""
<style>
/* Modern AI Theme - LIGHT VERSION */
.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    background-size: cover;
    background-attachment: fixed;
}

/* Glass effect container - LIGHTER */
.main .block-container {
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(10px);
    border-radius: 25px;
    padding: 2.5rem;
    margin-top: 2rem;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.5);
}

/* DARK TEXT for visibility */
h1, h2, h3, h4, h5, h6 {
    color: #1a1a1a !important;
    font-weight: 700 !important;
}

/* Normal text - DARK */
.stMarkdown, .stText, p, div {
    color: #333333 !important;
}

/* Button text - WHITE */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white !important;
    border: none;
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
    font-size: 16px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

/* Sidebar - LIGHT theme */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
    border-right: 1px solid #e0e0e0;
}

/* Sidebar text - DARK */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stButton > button {
    color: #1a1a1a !important;
}

/* Metrics cards - with WHITE text */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white !important;
    border-radius: 15px;
    padding: 1.5rem;
    border: none;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

/* Metrics text specifically */
[data-testid="metric-container"] * {
    color: white !important;
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 1rem;
    background: rgba(255, 255, 255, 0.9);
    padding: 10px;
    border-radius: 12px;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255, 255, 255, 0.7);
    border-radius: 8px;
    padding: 12px 24px;
    color: #333333 !important;
    font-weight: 500;
    transition: all 0.3s;
    border: 1px solid #e0e0e0;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* Chat bubbles */
.stChatMessage {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 18px;
    padding: 1.2rem;
    margin: 0.8rem 0;
    border: 1px solid rgba(102, 126, 234, 0.2);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    color: #333333 !important;
}

/* File uploader */
.stFileUploader > div > div {
    background: rgba(255, 255, 255, 0.95);
    border: 3px dashed #667eea;
    border-radius: 20px;
    padding: 3rem;
    text-align: center;
    transition: all 0.3s;
    color: #333333 !important;
}

.stFileUploader > div > div:hover {
    border-color: #764ba2;
    background: rgba(255, 255, 255, 0.95);
}

/* Progress bars */
.stProgress > div > div > div {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Expander styling */
div[data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 15px;
    border: 1px solid rgba(102, 126, 234, 0.2);
}

/* Success/Info/Warning boxes */
.stAlert {
    border-radius: 12px;
    border: none;
    background: rgba(255, 255, 255, 0.9);
}

/* Dataframe styling */
[data-testid="stDataFrame"] {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 12px;
}

/* Text input styling */
.stTextInput > div > div > input,
.stSelectbox > div > div > select,
.stNumberInput > div > div > input {
    background: #ffffff !important;
    border-radius: 10px;
    border: 2px solid #e5e7eb;
    padding: 10px;
    color: #000000 !important;
}

.stTextInput > div > div > input:focus,
.stSelectbox > div > div > select:focus,
.stNumberInput > div > div > input:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.stTextInput > div > div > input::placeholder,
.stSelectbox > div > div > select::placeholder {
    color: #666666 !important;
}

/* Radio buttons */
.stRadio > div {
    background: rgba(255, 255, 255, 0.9);
    padding: 15px;
    border-radius: 12px;
    color: #333333 !important;
}

.stRadio label {
    color: #333333 !important;
}

/* Divider */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    margin: 2rem 0;
}

/* Make ALL text in the app dark by default */
* {
    color: #333333 !important;
}

/* Override specific elements that need white text */
.stButton > button,
.stTabs [aria-selected="true"],
[data-testid="metric-container"] * {
    color: white !important;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #5a6fd8 0%, #6a3f9e 100%);
}
</style>
""", unsafe_allow_html=True)

# ========== SESSION STATE ==========
if 'contracts' not in st.session_state:
    st.session_state.contracts = []

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'vin_data' not in st.session_state:
    st.session_state.vin_data = {}

# ========== SIMULATED AI FUNCTIONS ==========
class SimpleContractAnalyzer:
    def analyze_contract_text(self, text):
        """Simulated contract analysis"""
        return {
            "interest_rate": "5.9%",
            "monthly_payment": "$450",
            "lease_term": "36 months",
            "down_payment": "$2,500",
            "mileage_limit": "12,000 miles/year",
            "residual_value": "$15,000",
            "excess_mileage_charge": "$0.25/mile",
            "early_termination_fee": "$350",
            "purchase_option": "Yes, at residual value",
            "warranty": "3 years/36,000 miles",
            "insurance_required": "Full coverage",
            "fairness_score": 78,
            "red_flags": ["High early termination fee", "Above average interest rate"],
            "recommendations": [
                "Negotiate interest rate to 4.5-5.0%",
                "Request $0 down payment option",
                "Ask for free maintenance for first year"
            ]
        }
    
    def calculate_fair_price(self, make, model, year):
        """Simulated price calculation"""
        prices = {
            "TOYOTA CAMRY 2023": {"fair": 28000, "range": [26000, 30000]},
            "HONDA ACCORD 2023": {"fair": 29000, "range": [27000, 31000]},
            "BMW 3 SERIES 2023": {"fair": 45000, "range": [42000, 48000]},
            "TESLA MODEL 3 2023": {"fair": 42000, "range": [40000, 44000]},
        }
        
        key = f"{make.upper()} {model.upper()} {year}"
        return prices.get(key, {"fair": 35000, "range": [33000, 37000]})

class NegotiationAI:
    def get_advice(self, issue):
        """Simulated negotiation advice"""
        advice_map = {
            "interest": "Research shows current market rates are 4-5%. Mention competitor offers.",
            "down_payment": "Many dealers offer $0 down promotions. Ask about current offers.",
            "mileage": "Average American drives 13,500 miles/year. Request at least 12,000.",
            "termination": "Early termination fees are negotiable. Target $200-300 range.",
            "warranty": "Request extended warranty or maintenance package as deal sweetener.",
            "general": "Be confident, do your research, and be willing to walk away if needed."
        }
        
        for key in advice_map:
            if key in issue.lower():
                return advice_map[key]
        
        return advice_map["general"]
    
    def generate_email(self, dealer_name, issues):
        """Generate negotiation email"""
        email = f"""Dear {dealer_name},

I've reviewed the lease proposal and would like to discuss the following points:

"""
        
        if "interest" in issues.lower():
            email += "• The interest rate seems higher than current market rates\n"
        if "down" in issues.lower():
            email += "• The down payment amount is higher than expected\n"
        if "mileage" in issues.lower():
            email += "• The mileage allowance may not suit my driving needs\n"
        
        email += """
I'm confident we can reach a mutually beneficial agreement. Please let me know when we can discuss these points.

Best regards,
[Your Name]
"""
        return email

# Initialize AI modules
analyzer = SimpleContractAnalyzer()
negotiator = NegotiationAI()

# ========== SIDEBAR ==========
with st.sidebar:
    # Logo and Title
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://emojicdn.elk.sh/🤖", width=50)
    with col2:
        st.markdown("<h2 style='margin:0;'>Car Lease AI</h2>", unsafe_allow_html=True)
        st.caption("Negotiation Assistant")
    
    st.markdown("---")
    
    # Navigation
    menu = st.radio(
        "**Main Menu**",
        ["🏠 Dashboard", "📄 Contract Analysis", "🤖 Negotiation AI", "💰 Price Check", "🚗 VIN Decoder", "📊 Reports"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # User Profile
    st.markdown("### 👤 User Profile")
    st.write("**Role:** Customer")
    st.write("**Credit Score:** 720")
    st.write("**Location:** New York")
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    if st.button("🆕 New Analysis", use_container_width=True, type="secondary"):
        st.session_state.contracts = []
        st.session_state.chat_history = []
        st.rerun()
    
    if st.button("📧 Export Report", use_container_width=True, type="secondary"):
        st.success("Report exported successfully!")
    
    st.markdown("---")
    st.caption("© 2024 Car Lease AI Assistant v1.0")

# ========== MAIN CONTENT ==========
if menu == "🏠 Dashboard":
    st.title("🤖 Car Lease AI Assistant")
    st.markdown("### AI-Powered Contract Review & Negotiation Platform")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Contracts Analyzed", "24", "+8")
    with col2:
        st.metric("Avg. Savings", "$3,200", "+18%")
    with col3:
        st.metric("Success Rate", "92%", "+5%")
    with col4:
        st.metric("User Rating", "4.8/5", "⭐")
    
    st.markdown("---")
    
    # Features
    st.subheader("🎯 Core Features")
    
    features = [
        {"icon": "📄", "title": "SLA Extraction", "desc": "AI extracts key contract terms automatically"},
        {"icon": "🤖", "title": "Negotiation AI", "desc": "Chat-based assistant for dealer negotiations"},
        {"icon": "💰", "title": "Price Analysis", "desc": "Fair market value comparison"},
        {"icon": "🚗", "title": "VIN Decoder", "desc": "Vehicle history and recall checks"},
        {"icon": "⚠️", "title": "Red Flag Detection", "desc": "Identifies risky contract terms"},
        {"icon": "📊", "title": "Fairness Scoring", "desc": "Overall contract quality assessment"},
    ]
    
    cols = st.columns(3)
    for idx, feature in enumerate(features):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"### {feature['icon']} {feature['title']}")
                st.write(feature['desc'])
                st.progress(0.9 - (idx * 0.05))
    
    st.markdown("---")
    
    # Quick Start
    st.subheader("🚀 Get Started")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📤 Upload Contract", use_container_width=True, type="primary"):
            st.success("Redirecting to Contract Analysis...")
    with col2:
        if st.button("🤖 Start Negotiation", use_container_width=True, type="primary"):
            st.success("Opening Negotiation AI...")

elif menu == "📄 Contract Analysis":
    st.title("📄 Contract Analysis")
    st.markdown("Upload your lease contract for AI-powered analysis")
    
    tab1, tab2, tab3 = st.tabs(["📤 Upload", "🔍 Analysis", "📋 Summary"])
    
    with tab1:
        st.subheader("Upload Contract Document")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a file (PDF, DOCX, TXT) or enter contract details manually",
            type=['txt', 'pdf', 'docx'],
            help="For demo, you can also enter details manually below"
        )
        
        # Manual input option
        with st.expander("📝 Or Enter Contract Details Manually"):
            col1, col2 = st.columns(2)
            with col1:
                interest_rate = st.number_input("Interest Rate (%)", 0.0, 20.0, 5.9, 0.1)
                monthly_payment = st.number_input("Monthly Payment ($)", 0, 2000, 450)
                lease_term = st.selectbox("Lease Term", [24, 36, 48, 60])
                down_payment = st.number_input("Down Payment ($)", 0, 10000, 2500)
            
            with col2:
                mileage_limit = st.number_input("Annual Mileage Limit", 5000, 20000, 12000, 1000)
                excess_charge = st.number_input("Excess Mileage Charge ($/mile)", 0.0, 1.0, 0.25, 0.05)
                termination_fee = st.number_input("Early Termination Fee ($)", 0, 1000, 350)
                warranty = st.selectbox("Warranty", ["3 years/36k miles", "5 years/60k miles", "None"])
        
        if st.button("Analyze Contract", type="primary", use_container_width=True):
            # Simulate analysis
            analysis = analyzer.analyze_contract_text("")
            st.session_state.contract_analysis = analysis
            st.success("✅ Contract analysis complete!")
            st.balloons()
    
    with tab2:
        if 'contract_analysis' in st.session_state:
            analysis = st.session_state.contract_analysis
            
            st.subheader("📊 Contract Analysis Results")
            
            # Key metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Fairness Score", f"{analysis['fairness_score']}/100")
            with col2:
                st.metric("Interest Rate", analysis['interest_rate'])
            with col3:
                st.metric("Monthly Payment", analysis['monthly_payment'])
            
            st.markdown("---")
            
            # Contract terms
            st.subheader("📝 Extracted Contract Terms")
            terms_df = pd.DataFrame([
                {"Term": "Lease Term", "Value": analysis['lease_term']},
                {"Term": "Down Payment", "Value": analysis['down_payment']},
                {"Term": "Mileage Limit", "Value": analysis['mileage_limit']},
                {"Term": "Residual Value", "Value": analysis['residual_value']},
                {"Term": "Purchase Option", "Value": analysis['purchase_option']},
                {"Term": "Warranty", "Value": analysis['warranty']},
            ])
            st.dataframe(terms_df, use_container_width=True, hide_index=True)
    
    with tab3:
        if 'contract_analysis' in st.session_state:
            analysis = st.session_state.contract_analysis
            
            st.subheader("⚠️ Red Flags")
            for flag in analysis['red_flags']:
                st.error(f"• {flag}")
            
            st.subheader("💡 Recommendations")
            for rec in analysis['recommendations']:
                st.success(f"• {rec}")
            
            # Download report
            report = f"""
            Car Lease Contract Analysis Report
            ===================================
            
            Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Summary:
            • Fairness Score: {analysis['fairness_score']}/100
            • Interest Rate: {analysis['interest_rate']}
            • Monthly Payment: {analysis['monthly_payment']}
            • Lease Term: {analysis['lease_term']}
            
            Red Flags:
            {chr(10).join(['• ' + flag for flag in analysis['red_flags']])}
            
            Recommendations:
            {chr(10).join(['• ' + rec for rec in analysis['recommendations']])}
            """
            
            st.download_button(
                "📥 Download Full Report",
                report,
                "contract_analysis_report.txt",
                "text/plain"
            )

elif menu == "🤖 Negotiation AI":
    st.title("🤖 Negotiation AI Assistant")
    st.markdown("Chat with AI to prepare for dealer negotiations")
    
    # Chat interface
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hi! I'm your negotiation assistant. How can I help you negotiate your car lease today?"}
        ]
    
    # Display chat messages
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask negotiation advice..."):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate AI response
        ai_response = negotiator.get_advice(prompt)
        st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
        with st.chat_message("assistant"):
            st.write(ai_response)
    
    st.markdown("---")
    
    # Quick questions
    st.subheader("💡 Quick Questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Lower interest rate?", use_container_width=True):
            st.session_state.chat_messages.append({"role": "user", "content": "How to negotiate lower interest rate?"})
            st.session_state.chat_messages.append({"role": "assistant", "content": negotiator.get_advice("interest")})
            st.rerun()
    
    with col2:
        if st.button("Reduce down payment?", use_container_width=True):
            st.session_state.chat_messages.append({"role": "user", "content": "How to reduce down payment?"})
            st.session_state.chat_messages.append({"role": "assistant", "content": negotiator.get_advice("down_payment")})
            st.rerun()
    
    with col3:
        if st.button("Increase mileage?", use_container_width=True):
            st.session_state.chat_messages.append({"role": "user", "content": "How to increase mileage allowance?"})
            st.session_state.chat_messages.append({"role": "assistant", "content": negotiator.get_advice("mileage")})
            st.rerun()
    
    # Email generator
    st.markdown("---")
    st.subheader("📧 Generate Negotiation Email")
    
    with st.form("email_form"):
        dealer_name = st.text_input("Dealer Name", "Sales Manager")
        issues = st.multiselect(
            "Issues to Address",
            ["High Interest Rate", "Large Down Payment", "Low Mileage Allowance", "Early Termination Fee"]
        )
        
        if st.form_submit_button("Generate Email"):
            email_text = negotiator.generate_email(dealer_name, ", ".join(issues))
            st.text_area("Email Template", email_text, height=200)
            
            st.download_button(
                "📥 Download Email",
                email_text,
                "negotiation_email.txt",
                "text/plain"
            )

elif menu == "💰 Price Check":
    st.title("💰 Fair Price Analysis")
    st.markdown("Check fair market value for your vehicle")
    
    # Vehicle details
    col1, col2, col3 = st.columns(3)
    with col1:
        make = st.selectbox("Make", ["Toyota", "Honda", "BMW", "Tesla", "Ford", "Mercedes"])
        model = st.text_input("Model", "Camry")
    with col2:
        year = st.selectbox("Year", list(range(2024, 2018, -1)))
        trim = st.text_input("Trim", "LE")
    with col3:
        mileage = st.number_input("Mileage", 0, 200000, 15000)
        condition = st.select_slider("Condition", ["Poor", "Fair", "Good", "Excellent"], value="Good")
    
    if st.button("Check Price", type="primary", use_container_width=True):
        # Get price analysis
        price_data = analyzer.calculate_fair_price(make, model, str(year))
        
        st.success("✅ Price analysis complete!")
        
        # Display results
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Fair Market Value", f"${price_data['fair']:,}")
        with col2:
            st.metric("Price Range", f"${price_data['range'][0]:,} - ${price_data['range'][1]:,}")
        with col3:
            diff = price_data['fair'] - 35000  # Example comparison
            st.metric("Vs. Average", f"${diff:+,}")
        
        # Price comparison chart
        st.subheader("📊 Price Comparison")
        fig_data = pd.DataFrame({
            "Category": ["Dealer Price", "Fair Price", "Market Low", "Market High"],
            "Price": [35000, price_data['fair'], price_data['range'][0], price_data['range'][1]]
        })
        
        import plotly.express as px
        fig = px.bar(fig_data, x='Category', y='Price', color='Category',
                    title="Price Comparison Analysis")
        st.plotly_chart(fig, use_container_width=True)

elif menu == "🚗 VIN Decoder":
    st.title("🚗 VIN Decoder & Vehicle History")
    
    vin = st.text_input("Enter VIN Number", "1HGCM82633A123456").upper()
    
    if st.button("Decode VIN", type="primary"):
        # Simulated VIN data
        vin_data = {
            "vin": vin,
            "make": "HONDA",
            "model": "ACCORD",
            "year": "2003",
            "engine": "2.4L L4 DOHC 16V",
            "fuel_type": "Gasoline",
            "body_class": "Sedan/Saloon",
            "manufacturer": "HONDA MOTOR CO., LTD",
            "plant": "MARYSVILLE, OHIO, UNITED STATES (USA)",
            "series": "ACCORD SEDAN 4-DR",
            "trim": "EX",
            "doors": "4",
            "recalls": "2 recall(s) found",
            "last_update": "2023-10-15"
        }
        
        st.session_state.vin_data = vin_data
        st.success("✅ VIN decoded successfully!")
    
    if st.session_state.vin_data:
        data = st.session_state.vin_data
        
        # Vehicle info
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🚘 Vehicle Information")
            st.write(f"**Make:** {data['make']}")
            st.write(f"**Model:** {data['model']}")
            st.write(f"**Year:** {data['year']}")
            st.write(f"**Engine:** {data['engine']}")
        
        with col2:
            st.subheader("📋 Specifications")
            st.write(f"**Body Type:** {data['body_class']}")
            st.write(f"**Fuel Type:** {data['fuel_type']}")
            st.write(f"**Manufacturer:** {data['manufacturer']}")
            st.write(f"**Plant:** {data['plant']}")
        
        # Recalls
        st.subheader("⚠️ Recall Information")
        recalls = [
            {"ID": "23V-123", "Date": "2023-03-15", "Component": "Airbag", "Status": "Open"},
            {"ID": "22V-456", "Date": "2022-08-22", "Component": "Brakes", "Status": "Closed"},
        ]
        
        st.dataframe(pd.DataFrame(recalls), use_container_width=True)

elif menu == "📊 Reports":
    st.title("📊 Analysis Reports")
    
    # Generate sample report
    report_data = {
        "Contract Analysis": {
            "Fairness Score": 78,
            "Interest Rate": "5.9%",
            "Monthly Payment": "$450",
            "Status": "Needs Improvement"
        },
        "Price Analysis": {
            "Fair Market Value": "$28,000",
            "Dealer Price": "$30,500",
            "Savings Opportunity": "$2,500",
            "Status": "Good Deal"
        },
        "Negotiation Points": {
            "Key Issues": 3,
            "Success Probability": "85%",
            "Target Savings": "$3,200",
            "Status": "High Potential"
        }
    }
    
    # Display metrics
    for category, metrics in report_data.items():
        st.subheader(category)
        cols = st.columns(len(metrics))
        for idx, (key, value) in enumerate(metrics.items()):
            with cols[idx]:
                st.metric(key, value)
        st.markdown("---")
    
    # Download comprehensive report
    comprehensive_report = """
    COMPREHENSIVE CAR LEASE ANALYSIS REPORT
    ========================================
    
    Generated: {date}
    
    1. CONTRACT ANALYSIS
    --------------------
    • Fairness Score: 78/100
    • Interest Rate: 5.9% (Target: 4.5-5.0%)
    • Monthly Payment: $450
    • Lease Term: 36 months
    • Down Payment: $2,500
    
    2. PRICE ANALYSIS
    -----------------
    • Fair Market Value: $28,000
    • Dealer Price: $30,500
    • Potential Savings: $2,500
    • Price Rating: Good Deal
    
    3. NEGOTIATION STRATEGY
    -----------------------
    Key Issues to Address:
    1. Interest rate reduction (Target: 4.5%)
    2. Down payment reduction (Target: $2,000)
    3. Mileage allowance increase (Target: 12,000 miles)
    
    4. RECOMMENDATIONS
    ------------------
    1. Use competitor offers as leverage
    2. Request value-added services
    3. Be prepared to walk away
    4. Focus on total cost, not monthly payment
    
    AI Confidence Score: 92%
    Estimated Savings: $3,200
    """.format(date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    st.download_button(
        "📥 Download Comprehensive Report",
        comprehensive_report,
        "car_lease_analysis_report.txt",
        "text/plain",
        use_container_width=True
    )

# ========== FOOTER ==========
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🤖 Powered by AI")
with col2:
    st.caption("🔒 Secure & Private")
with col3:
    st.caption("© 2024 Car Lease AI Assistant")

# ========== RUN APP ==========
if __name__ == "__main__":
    pass