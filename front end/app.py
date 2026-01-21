import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==================== CONFIGURATION ====================
BACKEND_URL = "http://localhost:5000"  # Change this if your backend is on different URL/port

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Car Lease Assistant",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        padding: 10px;
        font-weight: bold;
    }
    
    .upload-success {
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 20px;
        background-color: #f8fff8;
        margin: 10px 0;
    }
    
    .chat-bubble {
        padding: 12px 18px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 80%;
    }
    
    .user-bubble {
        background-color: #007bff;
        color: white;
        margin-left: auto;
    }
    
    .assistant-bubble {
        background-color: #f1f1f1;
        color: #333;
        margin-right: auto;
    }
</style>
""", unsafe_allow_html=True)

# ==================== API FUNCTIONS ====================
def upload_file_to_backend(file):
    """Upload file to backend"""
    try:
        files = {'file': (file.name, file.getvalue(), file.type)}
        response = requests.post(f"{BACKEND_URL}/api/upload", files=files)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def upload_text_to_backend(text):
    """Upload text to backend"""
    try:
        data = {"text": text}
        response = requests.post(f"{BACKEND_URL}/api/upload-text", json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def get_all_contracts():
    """Get all contracts from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/contracts")
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to get contracts: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def send_chat_message(message, contract_id=None):
    """Send chat message to backend"""
    try:
        data = {"message": message}
        if contract_id:
            data["contract_id"] = contract_id
            
        response = requests.post(f"{BACKEND_URL}/api/chat", json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "response": "I'm having trouble connecting. Please try again."}
    except Exception as e:
        return {"success": False, "response": "Backend connection failed. Please make sure the backend server is running."}

def lookup_vehicle(vin=None, make=None, model=None, year=None):
    """Lookup vehicle information"""
    try:
        data = {}
        if vin:
            data["vin"] = vin
        if make:
            data["make"] = make
        if model:
            data["model"] = model
        if year:
            data["year"] = year
            
        response = requests.post(f"{BACKEND_URL}/api/vehicle/lookup", json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "vehicle": {}}
    except Exception as e:
        return {"success": False, "vehicle": {}}

# ==================== SESSION STATE ====================
if 'contracts' not in st.session_state:
    st.session_state.contracts = []

if 'current_contract' not in st.session_state:
    st.session_state.current_contract = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "👋 Welcome! I'm your car negotiation assistant. Upload a contract or ask me anything about car leases!"}
    ]

if 'vehicle_data' not in st.session_state:
    st.session_state.vehicle_data = None

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

# ==================== PAGES ====================
def upload_page():
    st.title("📄 Upload Contract")
    
    tab1, tab2, tab3 = st.tabs(["📤 Upload File", "📝 Paste Text", "📋 Try Sample"])
    
    with tab1:
        st.subheader("Upload Your Contract File")
        
        uploaded_file = st.file_uploader(
            "Choose a file (PDF, Image, TXT)",
            type=['pdf', 'png', 'jpg', 'jpeg', 'txt'],
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"**File:** {uploaded_file.name}")
                st.info(f"**Size:** {len(uploaded_file.getvalue()) / 1024:.1f} KB")
            
            with col2:
                if st.button("🚀 Process with Backend", type="primary", use_container_width=True):
                    with st.spinner("Uploading to backend..."):
                        result = upload_file_to_backend(uploaded_file)
                        
                        if result and result.get('success'):
                            contract = result['contract']
                            st.session_state.contracts.append(contract)
                            st.session_state.current_contract = contract
                            
                            st.success("✅ Contract processed by backend!")
                            
                            # Show extracted data
                            with st.expander("📋 View Extracted Terms"):
                                sla = contract.get('sla_data', {})
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write("**Financial Terms:**")
                                    st.write(f"- APR: {sla.get('interest_rate', 'N/A')}%")
                                    st.write(f"- Monthly: ${sla.get('monthly_payment_amount', 'N/A')}")
                                    st.write(f"- Term: {sla.get('lease_term_months', 'N/A')} months")
                                
                                with col2:
                                    st.write("**Contract Details:**")
                                    st.write(f"- Mileage: {sla.get('mileage_allowance_per_year', 'N/A')} miles/yr")
                                    st.write(f"- Overage: ${sla.get('mileage_overage_charge_per_mile', 'N/A')}/mile")
                                    st.write(f"- Score: {contract.get('fairness_score', 'N/A')}/100")
                        
                        else:
                            st.error("Failed to process contract with backend")
    
    with tab2:
        st.subheader("Paste Contract Text")
        
        text_input = st.text_area(
            "Paste your contract text here:",
            height=200,
            placeholder="Example:\nVehicle: 2023 Honda Civic\nMonthly Payment: $299\nTerm: 60 months\nAPR: 5.2%\nDown Payment: $2,000"
        )
        
        if st.button("📤 Submit Text to Backend", use_container_width=True) and text_input:
            with st.spinner("Processing text..."):
                result = upload_text_to_backend(text_input)
                
                if result and result.get('success'):
                    contract = result['contract']
                    st.session_state.contracts.append(contract)
                    st.session_state.current_contract = contract
                    st.success("✅ Text processed by backend!")
    
    with tab3:
        st.subheader("Try Without Uploading")
        st.info("Test the system with sample data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Load Sample Contract", use_container_width=True):
                sample_contract = {
                    "id": 999,
                    "filename": "sample_contract.pdf",
                    "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "fairness_score": 75,
                    "sla_data": {
                        "interest_rate": "4.5",
                        "monthly_payment_amount": "349.00",
                        "lease_term_months": "36",
                        "mileage_allowance_per_year": "12000"
                    }
                }
                
                st.session_state.contracts.append(sample_contract)
                st.session_state.current_contract = sample_contract
                st.success("✅ Sample contract loaded!")
        
        with col2:
            if st.button("🔄 Refresh from Backend", use_container_width=True):
                result = get_all_contracts()
                if result and result.get('success'):
                    st.session_state.contracts = result.get('contracts', [])
                    st.success(f"✅ Loaded {len(st.session_state.contracts)} contracts from backend")

def analyze_page():
    st.title("🔍 Contract Analysis")
    
    if not st.session_state.current_contract:
        st.warning("No contract selected. Please upload a contract first.")
        return
    
    contract = st.session_state.current_contract
    sla = contract.get('sla_data', {})
    
    # Header
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Contract", contract.get('filename', 'Unknown'))
    with col2:
        st.metric("Upload Date", contract.get('upload_date', 'Today'))
    with col3:
        score = contract.get('fairness_score', 0)
        color = "green" if score > 70 else "orange" if score > 50 else "red"
        st.markdown(f"**Score:** <span style='color:{color}; font-size:24px'>{score}/100</span>", unsafe_allow_html=True)
    
    st.divider()
    
    # Analysis
    tab1, tab2, tab3 = st.tabs(["📊 Terms", "💰 Payments", "📈 Market"])
    
    with tab1:
        if sla:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Financial Terms")
                st.write(f"**APR:** {sla.get('interest_rate', 'N/A')}%")
                st.write(f"**Monthly Payment:** ${sla.get('monthly_payment_amount', 'N/A')}")
                st.write(f"**Term:** {sla.get('lease_term_months', 'N/A')} months")
                st.write(f"**Down Payment:** ${sla.get('down_payment_amount', 'N/A')}")
            
            with col2:
                st.subheader("Contract Details")
                st.write(f"**Mileage Allowance:** {sla.get('mileage_allowance_per_year', 'N/A')} miles/year")
                st.write(f"**Overage Charge:** ${sla.get('mileage_overage_charge_per_mile', 'N/A')}/mile")
                st.write(f"**Residual Value:** ${sla.get('residual_value', 'N/A')}")
                st.write(f"**Buyout Price:** ${sla.get('purchase_option_price', 'N/A')}")
    
    with tab2:
        if sla.get('monthly_payment_amount') and sla.get('lease_term_months'):
            monthly = float(sla['monthly_payment_amount'])
            term = int(sla['lease_term_months'])
            
            # Payment chart
            months = list(range(1, term + 1))
            payments = [monthly] * term
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=months, y=payments,
                mode='lines+markers',
                name='Monthly Payment'
            ))
            
            fig.update_layout(
                title=f"Total Payments: ${monthly * term:,.2f}",
                xaxis_title="Month",
                yaxis_title="Amount ($)"
            )
            
            st.plotly_chart(fig, use_container_width=True)

def chat_page():
    st.title("💬 Negotiation Assistant")
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-bubble user-bubble">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble assistant-bubble">{message["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Ask me about negotiation strategies...")
    
    if user_input:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Get contract ID if available
        contract_id = st.session_state.current_contract.get('id') if st.session_state.current_contract else None
        
        # Get response from backend
        with st.spinner("Thinking..."):
            result = send_chat_message(user_input, contract_id)
            
            if result.get('success'):
                response = result['response']
            else:
                response = "I'm currently unavailable. Please try again later."
        
        # Add assistant response
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Rerun to show new messages
        st.rerun()

def vehicle_page():
    st.title("🚗 Vehicle Lookup")
    
    tab1, tab2 = st.tabs(["VIN Lookup", "Manual Search"])
    
    with tab1:
        vin = st.text_input("Enter VIN (17 characters):", placeholder="1HGCM82633A123456")
        
        if st.button("🔍 Lookup with Backend", use_container_width=True) and vin:
            with st.spinner("Searching..."):
                result = lookup_vehicle(vin=vin)
                
                if result and result.get('success'):
                    st.session_state.vehicle_data = result['vehicle']
                    st.success("✅ Vehicle found!")
    
    with tab2:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            make = st.text_input("Make", placeholder="Toyota")
        
        with col2:
            model = st.text_input("Model", placeholder="Camry")
        
        with col3:
            year = st.selectbox("Year", list(range(2024, 2014, -1)))
        
        if st.button("🔍 Search with Backend", use_container_width=True) and make and model:
            with st.spinner("Searching..."):
                result = lookup_vehicle(make=make, model=model, year=year)
                
                if result and result.get('success'):
                    st.session_state.vehicle_data = result['vehicle']
                    st.success("✅ Vehicle data found!")
    
    # Display vehicle data
    if st.session_state.vehicle_data:
        st.divider()
        st.subheader("Vehicle Information")
        
        vehicle = st.session_state.vehicle_data
        
        col1, col2 = st.columns(2)
        
        with col1:
            for key in ['make', 'model', 'year', 'body_style', 'engine']:
                if key in vehicle and vehicle[key]:
                    st.write(f"**{key.title()}:** {vehicle[key]}")
        
        with col2:
            if 'pricing' in vehicle:
                st.write("**Pricing:**")
                for source, price in vehicle['pricing'].items():
                    st.write(f"- {source.title()}: ${price:,}")
            
            if 'recalls' in vehicle:
                st.write(f"**Recalls:** {len(vehicle['recalls'])}")

def dashboard_page():
    st.title("📊 Dashboard")
    
    # Stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Contracts", len(st.session_state.contracts))
    
    with col2:
        if st.session_state.contracts:
            avg_score = sum(c.get('fairness_score', 0) for c in st.session_state.contracts) / len(st.session_state.contracts)
            st.metric("Avg Score", f"{avg_score:.1f}")
        else:
            st.metric("Avg Score", "0")
    
    with col3:
        st.metric("Backend Status", "✅ Online" if test_backend() else "❌ Offline")
    
    st.divider()
    
    # Quick actions
    st.subheader("Quick Actions")
    
    cols = st.columns(4)
    
    with cols[0]:
        if st.button("📤 Upload", use_container_width=True):
            st.session_state.current_page = "Upload"
            st.rerun()
    
    with cols[1]:
        if st.button("🔍 Analyze", use_container_width=True):
            if st.session_state.current_contract:
                st.session_state.current_page = "Analyze"
                st.rerun()
            else:
                st.warning("Upload a contract first")
    
    with cols[2]:
        if st.button("💬 Chat", use_container_width=True):
            st.session_state.current_page = "Chat"
            st.rerun()
    
    with cols[3]:
        if st.button("🚗 Vehicle", use_container_width=True):
            st.session_state.current_page = "Vehicle"
            st.rerun()
    
    # Recent contracts
    if st.session_state.contracts:
        st.divider()
        st.subheader("Recent Contracts")
        
        for contract in st.session_state.contracts[-3:]:
            with st.expander(f"{contract.get('filename', 'Contract')}"):
                st.write(f"**Score:** {contract.get('fairness_score', 'N/A')}/100")
                st.write(f"**APR:** {contract.get('sla_data', {}).get('interest_rate', 'N/A')}%")

def test_backend():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False

# ==================== MAIN APP ====================
def main():
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3073/3073721.png", width=100)
        st.title("Car Lease Assistant")
        
        # Backend status
        backend_status = test_backend()
        if backend_status:
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Offline")
            st.info("Start backend: python app.py")
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["Dashboard", "Upload", "Analyze", "Chat", "Vehicle"],
            index=["Dashboard", "Upload", "Analyze", "Chat", "Vehicle"].index(st.session_state.current_page)
        )
        
        st.session_state.current_page = page
        
        st.divider()
        
        # Quick info
        st.write(f"**Contracts:** {len(st.session_state.contracts)}")
        
        if st.session_state.current_contract:
            st.write(f"**Current Score:** {st.session_state.current_contract.get('fairness_score', 'N/A')}/100")
        
        st.divider()
        
        # Backend controls
        if st.button("🔄 Refresh Contracts", use_container_width=True):
            result = get_all_contracts()
            if result and result.get('success'):
                st.session_state.contracts = result.get('contracts', [])
                st.rerun()
        
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.contracts = []
            st.session_state.current_contract = None
            st.session_state.chat_history = [
                {"role": "assistant", "content": "👋 Chat cleared! How can I help you?"}
            ]
            st.rerun()
    
    # Page routing
    if page == "Dashboard":
        dashboard_page()
    elif page == "Upload":
        upload_page()
    elif page == "Analyze":
        analyze_page()
    elif page == "Chat":
        chat_page()
    elif page == "Vehicle":
        vehicle_page()

if __name__ == "__main__":
    main()