
import streamlit as st

import sys
import subprocess
import os

def install_package(package):
    """Install a Python package"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
        print(f"✅ {package} installed")
        return True
    except:
        print(f"⚠️  Could not install {package}, trying alternative...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--user", "--quiet"])
            print(f"✅ {package} installed for user")
            return True
        except:
            print(f"❌ Failed to install {package}")
            return False

def create_app():
    """Create the COMPLETE Streamlit app file with ALL features"""
    app_content = '''import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ====================================================
# PAGE CONFIGURATION
# ====================================================
st.set_page_config(
    page_title="Car Lease Contract Assistant",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================================================
# CUSTOM CSS
# ====================================================
st.markdown("""
<style>

/* ===== GLOBAL BACKGROUND ===== */
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #F8FAFF, #EEF2FF);
    color: #1E293B;
    font-family: "Segoe UI", sans-serif;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #DBEAFE, #EFF6FF);
}
[data-testid="stSidebar"] * {
    color: #1E293B !important;
}

/* ===== HEADINGS ===== */
h1 {
    color: #1D4ED8 !important;
    font-weight: 800;
}
h2 {
    color: #2563EB !important;
}
h3, h4 {
    color: #1E293B !important;
}

/* ===== NORMAL TEXT ===== */
p, span, label, li {
    color: #1E293B !important;
    font-size: 15px;
}

/* ===== METRIC BOXES ===== */
[data-testid="metric-container"] {
    background-color: #FFFFFF;
    border-radius: 14px;
    padding: 18px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
}
[data-testid="metric-container"] * {
    color: #1E293B !important;
    font-weight: 600;
}

/* ===== TABS ===== */
button[data-baseweb="tab"] {
    background-color: #E0E7FF;
    color: #1E293B !important;
    font-weight: 600;
    border-radius: 10px;
    margin-right: 6px;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background-color: #2563EB !important;
    color: #FFFFFF !important;
}

/* ===== CONTENT CARDS ===== */
.result-card {
    background-color: #FFFFFF;
    color: #1E293B;
    border-left: 6px solid #3B82F6;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 18px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
}

/* ===== RECALL WARNINGS ===== */
.recall-card {
    background-color: #FEFCE8;
    color: #854D0E;
    border-left: 6px solid #FACC15;
    border-radius: 12px;
    padding: 15px;
}
.recall-card.critical {
    background-color: #FEF2F2;
    color: #7F1D1D;
    border-left: 6px solid #EF4444;
}

/* ===== BUTTONS ===== */
.stButton > button {
    background: linear-gradient(90deg, #2563EB, #60A5FA);
    color: #FFFFFF;
    font-weight: 700;
    border-radius: 12px;
    padding: 10px 18px;
    border: none;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #1D4ED8, #3B82F6);
}

/* ===== FILE UPLOADER ===== */
[data-testid="stFileUploader"] {
    background-color: #FFFFFF;
    border: 2px dashed #93C5FD;
    padding: 22px;
    border-radius: 14px;
    color: #1E293B;
}

/* ===== CHAT MESSAGES ===== */
[data-testid="stChatMessage"] {
    background-color: #FFFFFF;
    border-radius: 14px;
    padding: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.05);
    color: #1E293B;
}

</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .progress-step {
        padding: 10px 20px;
        border-radius: 20px;
        margin: 5px;
        font-weight: bold;
    }
    .step-completed {
        background-color: #10B981;
        color: white;
    }
    .step-current {
        background-color: #3B82F6;
        color: white;
    }
    .result-card {
        padding: 20px;
        border-radius: 12px;
        background: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
        border-left: 5px solid #3B82F6;
    }
    .result-card.good {
        border-left-color: #10B981;
    }
    .recall-card {
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        background: #FEF3C7;
        border-left: 4px solid #F59E0B;
    }
    .recall-card.critical {
        background: #FEE2E2;
        border-left-color: #EF4444;
    }
</style>
""", unsafe_allow_html=True)

# ====================================================
# SESSION STATE
# ====================================================
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = {}
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "Hello! I'm your car lease negotiation assistant. Upload a contract to begin!"}
    ]

# ====================================================
# HELPER FUNCTIONS
# ====================================================
def get_recall_history(vin, make, model, year):
    """Generate recall history data"""
    recalls = []
    
    # Sample recall data based on vehicle
    if "honda" in make.lower() or "toyota" in make.lower():
        recalls = [
            {
                "id": "23V123000",
                "date": "2023-03-15",
                "component": "Software Update",
                "description": "Engine control module software may cause unexpected stalling",
                "severity": "High",
                "status": "Open",
                "critical": True
            },
            {
                "id": "22V456000",
                "date": "2022-08-20",
                "component": "Brake System",
                "description": "Brake pedal may feel soft or go to floor",
                "severity": "Medium",
                "status": "Fixed",
                "critical": False
            }
        ]
    elif "bmw" in make.lower() or "mercedes" in make.lower():
        recalls = [
            {
                "id": "23V789000",
                "date": "2023-05-10",
                "component": "Fuel System",
                "description": "Potential fuel leak in the engine compartment",
                "severity": "High",
                "status": "Open",
                "critical": True
            }
        ]
    else:
        recalls = [
            {
                "id": "23V999000",
                "date": "2023-01-15",
                "component": "Safety System",
                "description": "Airbag may not deploy properly in certain conditions",
                "severity": "High",
                "status": "Fixed",
                "critical": True
            }
        ]
    
    recall_summary = {
        "total_recalls": len(recalls),
        "open_recalls": len([r for r in recalls if r["status"] == "Open"]),
        "critical_recalls": len([r for r in recalls if r["critical"]]),
        "recall_rating": "Good" if len(recalls) == 0 else "Average" if len(recalls) <= 2 else "Poor"
    }
    
    return recalls, recall_summary

def get_market_analysis(make, model, year, monthly_payment, term_months):
    """Generate market price analysis"""
    # Base prices
    base_prices = {
        "honda": {"accord": 32000, "civic": 25000, "cr-v": 35000},
        "toyota": {"camry": 30000, "corolla": 23000, "rav4": 34000},
        "bmw": {"3 series": 45000, "x5": 65000},
        "ford": {"f-150": 42000, "escape": 28000}
    }
    
    make_key = make.lower()
    model_key = model.lower().replace(" ", "_")
    
    # Get base price
    base_price = 35000  # Default
    if make_key in base_prices:
        for key, price in base_prices[make_key].items():
            if key.replace(" ", "_") in model_key:
                base_price = price
                break
    
    # Adjust for year
    current_year = datetime.now().year
    age = current_year - year
    
    if age == 0:
        market_price = base_price
    elif age == 1:
        market_price = base_price * 0.85
    else:
        market_price = base_price * 0.75
    
    # Calculate fair monthly payment
    fair_monthly = (market_price - (market_price * 0.60)) / term_months
    fair_monthly += (market_price + (market_price * 0.60)) * 0.0025
    
    # Generate insights
    price_difference = monthly_payment - fair_monthly
    price_status = "Good" if price_difference <= 0 else "Fair" if price_difference <= 50 else "High"
    
    insights = [
        f"Market value: ${market_price:,.0f}",
        f"Fair monthly payment: ${fair_monthly:,.0f}",
        f"Your payment: ${monthly_payment:,.0f} ({'+' if price_difference > 0 else ''}${abs(price_difference):,.0f})"
    ]
    
    # Negotiation points
    negotiation_points = [
        {
            "point": "Price Adjustment",
            "current": f"${monthly_payment:,.0f}/month",
            "target": f"${fair_monthly:,.0f}/month",
            "savings": f"${price_difference * term_months:,.0f} total"
        },
        {
            "point": "APR Reduction",
            "current": "5.9%",
            "target": "5.0%",
            "savings": "$1,200 over lease"
        }
    ]
    
    return {
        "market_price": market_price,
        "fair_monthly_payment": fair_monthly,
        "price_difference": price_difference,
        "price_status": price_status,
        "insights": insights,
        "negotiation_points": negotiation_points,
        "price_comparison": {
            "your_deal": monthly_payment,
            "market_average": fair_monthly,
            "best_deal": fair_monthly * 0.95
        }
    }

def simulate_analysis():
    """Simulate the complete analysis process"""
    steps = [
        "📄 Extracting contract text...",
        "🔍 Identifying contract terms...",
        "🚗 Fetching vehicle details...",
        "⚠️ Checking recall history...",
        "📊 Analyzing market prices...",
        "🤖 Preparing negotiation insights..."
    ]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, step in enumerate(steps):
        status_text.text(step)
        progress_bar.progress((i + 1) / len(steps))
        time.sleep(0.8)
    
    return True

# ====================================================
# MAIN APP
# ====================================================
st.markdown('<h1 class="main-header">🚗 Car Lease Contract Assistant</h1>', unsafe_allow_html=True)
st.markdown("### AI-Powered Contract Analysis, Market Insights & Negotiation Assistant")

# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")
    enable_demo = st.checkbox("Use Demo Data", value=True)
    
    if st.button("🔄 Reset Analysis", use_container_width=True):
        st.session_state.uploaded_file = None
        st.session_state.analysis_complete = False
        st.session_state.analysis_data = {}
        st.rerun()

# Main Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload", "📋 Contract", "⚠️ Recalls", "📊 Market"])

# ====================================================
# TAB 1: UPLOAD
# ====================================================
with tab1:
    st.header("Upload Your Contract")
    
    uploaded_file = st.file_uploader(
        "Drag and drop or click to upload",
        type=['pdf', 'jpg', 'jpeg', 'png', 'txt'],
        help="Upload your car lease/loan contract"
    )
    
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
        
        if st.button("🔍 Start Complete Analysis", type="primary", use_container_width=True):
            with st.spinner("Analyzing your contract..."):
                # Simulate analysis
                simulate_analysis()
                
                # Generate analysis data
                st.session_state.analysis_data = {
                    "filename": uploaded_file.name,
                    "vin": "1HGCM82633A123456",
                    "make": "Honda",
                    "model": "Accord",
                    "year": 2023,
                    "monthly_payment": 450.00,
                    "apr": 5.9,
                    "term_months": 36,
                    "down_payment": 3000.00,
                    "mileage_allowance": 12000,
                    "overage_charge": 0.25,
                    "extracted_text": "VEHICLE LEASE AGREEMENT\\n\\nThis agreement is made between ABC Motors and John Doe...\\nMonthly Payment: $450.00\\nTerm: 36 months\\nAPR: 5.9%\\nMileage Allowance: 12,000 miles per year\\nOverage Charge: $0.25 per mile...",
                    "fairness_score": 78
                }
                
                # Get recall history
                recalls, recall_summary = get_recall_history(
                    st.session_state.analysis_data["vin"],
                    st.session_state.analysis_data["make"],
                    st.session_state.analysis_data["model"],
                    st.session_state.analysis_data["year"]
                )
                
                st.session_state.analysis_data["recalls"] = recalls
                st.session_state.analysis_data["recall_summary"] = recall_summary
                
                # Get market analysis
                market_analysis = get_market_analysis(
                    st.session_state.analysis_data["make"],
                    st.session_state.analysis_data["model"],
                    st.session_state.analysis_data["year"],
                    st.session_state.analysis_data["monthly_payment"],
                    st.session_state.analysis_data["term_months"]
                )
                
                st.session_state.analysis_data["market_analysis"] = market_analysis
                st.session_state.analysis_complete = True
                
                st.success("✅ Analysis Complete!")
                st.balloons()

# ====================================================
# TAB 2: CONTRACT DETAILS
# ====================================================
with tab2:
    st.header("Contract Analysis")
    
    if st.session_state.analysis_complete:
        data = st.session_state.analysis_data
        
        # Contract Score
        col1, col2 = st.columns([1, 2])
        with col1:
            score = data.get("fairness_score", 75)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Contract Score"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 60], 'color': "red"},
                        {'range': [60, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "green"}
                    ]
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Key Contract Terms")
            terms_col1, terms_col2 = st.columns(2)
            
            with terms_col1:
                st.metric("Monthly Payment", f"${data.get('monthly_payment', 0):,.2f}")
                st.metric("APR", f"{data.get('apr', 0)}%")
                st.metric("Down Payment", f"${data.get('down_payment', 0):,.0f}")
            
            with terms_col2:
                st.metric("Term", f"{data.get('term_months', 0)} months")
                st.metric("Mileage Allowance", f"{data.get('mileage_allowance', 0):,} miles/year")
                st.metric("Overage Charge", f"${data.get('overage_charge', 0):.2f}/mile")
        
        # Vehicle Details
        st.markdown("### Vehicle Information")
        vehicle_cols = st.columns(4)
        with vehicle_cols[0]:
            st.metric("VIN", data.get("vin", "N/A"))
        with vehicle_cols[1]:
            st.metric("Make", data.get("make", "N/A"))
        with vehicle_cols[2]:
            st.metric("Model", data.get("model", "N/A"))
        with vehicle_cols[3]:
            st.metric("Year", data.get("year", "N/A"))
    else:
        st.info("📤 Please upload and analyze a contract first")

# ====================================================
# TAB 3: RECALLS & SAFETY
# ====================================================
with tab3:
    st.header("⚠️ Recall History & Safety Check")
    
    if st.session_state.analysis_complete:
        data = st.session_state.analysis_data
        recalls = data.get("recalls", [])
        recall_summary = data.get("recall_summary", {})
        
        # Recall Summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Recalls", recall_summary.get("total_recalls", 0))
        with col2:
            st.metric("Open Recalls", recall_summary.get("open_recalls", 0))
        with col3:
            st.metric("Critical Recalls", recall_summary.get("critical_recalls", 0))
        with col4:
            st.metric("Recall Rating", recall_summary.get("recall_rating", "Unknown"))
        
        # Safety Status
        if recall_summary.get("critical_recalls", 0) > 0:
            st.error("🚨 CRITICAL: This vehicle has open safety recalls!")
        elif recall_summary.get("open_recalls", 0) > 0:
            st.warning("⚠️ WARNING: This vehicle has open recalls")
        else:
            st.success("✅ GOOD: No open safety recalls")
        
        # Detailed Recall List
        if recalls:
            st.subheader("Recall Details")
            for recall in recalls:
                recall_class = "recall-card critical" if recall.get("critical") else "recall-card"
                st.markdown(f'<div class="{recall_class}">', unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{recall.get('component', 'Unknown Component')}**")
                    st.markdown(f"*{recall.get('description', 'No description')}*")
                with col2:
                    st.markdown(f"**Date:** {recall.get('date', 'Unknown')}")
                    st.markdown(f"**Severity:** {recall.get('severity', 'Unknown')}")
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("📋 No recall history found")
    else:
        st.info("📤 Please upload and analyze a contract first")

# ====================================================
# TAB 4: MARKET ANALYSIS
# ====================================================
with tab4:
    st.header("📊 Market Price Analysis")
    
    if st.session_state.analysis_complete:
        data = st.session_state.analysis_data
        market_data = data.get("market_analysis", {})
        
        # Price Comparison
        st.subheader("Price Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Price chart
            prices = market_data.get("price_comparison", {})
            if prices:
                fig = go.Figure(data=[
                    go.Bar(
                        x=['Your Deal', 'Market Average', 'Best Deal'],
                        y=[prices.get('your_deal', 0), prices.get('market_average', 0), prices.get('best_deal', 0)],
                        marker_color=['#EF4444', '#3B82F6', '#10B981']
                    )
                ])
                fig.update_layout(
                    title="Monthly Payment Comparison",
                    yaxis_title="Monthly Payment ($)",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Price insights
            st.markdown("### Market Insights")
            for insight in market_data.get("insights", []):
                st.info(f"💡 {insight}")
            
            # Price status
            price_status = market_data.get("price_status", "Unknown")
            if price_status == "Good":
                st.success("✅ You're getting a good deal!")
            elif price_status == "Fair":
                st.warning("⚠️ Price is fair, but could be better")
            else:
                st.error("❌ Price is above market average")
        
        # Negotiation Points
        st.subheader("Negotiation Strategy")
        
        negotiation_points = market_data.get("negotiation_points", [])
        for point in negotiation_points:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{point.get('point', '')}**")
            with col2:
                st.metric("Current", point.get('current', ''))
            with col3:
                st.metric("Target", point.get('target', ''))
            
            st.markdown(f"**Potential Savings:** {point.get('savings', '')}")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("📤 Please upload and analyze a contract first")

# ====================================================
# NEGOTIATION CHAT
# ====================================================
st.markdown("---")
st.header("🤖 Negotiation Assistant")

# Display chat
for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Ask about your contract negotiation..."):
    # Add user message
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            time.sleep(1)
            
            # Simple AI responses
            if "apr" in prompt.lower():
                response = f"Your APR is {st.session_state.analysis_data.get('apr', 0)}%. Market average is 5.5%. Ask for 5.0%."
            elif "mileage" in prompt.lower():
                response = f"Your mileage allowance is {st.session_state.analysis_data.get('mileage_allowance', 0):,} miles/year. Ask for 15,000 miles/year."
            elif "recall" in prompt.lower():
                if st.session_state.analysis_complete:
                    recall_summary = st.session_state.analysis_data.get("recall_summary", {})
                    response = f"This vehicle has {recall_summary.get('total_recalls', 0)} recalls. Use this as negotiation leverage."
                else:
                    response = "Please analyze a contract first to check recall history."
            else:
                response = "I can help with APR, mileage, price, and recall negotiations. What specific area would you like help with?"
            
            st.write(response)
            st.session_state.chat_messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.caption("Car Lease Contract Assistant v2.0 | Complete with Recall History & Market Analysis")
'''
    
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(app_content)
    print("✅ app.py created successfully")

def main():
    print("=" * 50)
    print("🚗 CAR LEASE CONTRACT ASSISTANT SETUP")
    print("=" * 50)
    
    # Check Python
    try:
        python_version = subprocess.check_output([sys.executable, "--version"]).decode().strip()
        print(f"✅ Python detected: {python_version}")
    except:
        print("❌ Python not found!")
        print("Please install Python from: https://www.python.org/downloads/")
        input("Press Enter to exit...")
        return
    
    # Install requirements
    print("\n📦 Installing required packages...")
    packages = ["streamlit", "pandas", "plotly", "pillow"]
    
    for package in packages:
        install_package(package)
    
    # Create app file
    print("\n📄 Creating application...")
    create_app()
    
    # Run the app
    print("\n" + "=" * 50)
    print("🚀 STARTING CAR LEASE ASSISTANT...")
    print("=" * 50)
    print("\nThe app will open in your browser automatically.")
    print("If it doesn't open, go to: http://localhost:8501")
    print("\nPress Ctrl+C to stop the application.")
    
    # Run streamlit
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTrying alternative method...")
        
        # Try direct import
        try:
            print("Running app directly...")
            import streamlit.web.bootstrap as bootstrap
            bootstrap.run("app.py", "", [], {})
        except:
            print("Failed to run. Please run manually: python -m streamlit run app.py")

if __name__ == "__main__":
    main()
