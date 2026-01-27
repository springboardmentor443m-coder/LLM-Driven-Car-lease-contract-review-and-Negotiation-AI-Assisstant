import streamlit as st
import pandas as pd
import requests
import os
import re
from typing import Optional, Dict, Any
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import io
import base64

# ================== API CONFIGURATION ==================
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def check_api_connection() -> bool:
    """Check if FastAPI backend is available."""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

# ================== API CLIENT FUNCTIONS ==================
def api_extract_contract(uploaded_file) -> Dict[str, Any]:
    """Extract contract data via FastAPI /extract endpoint."""
    try:
        uploaded_file.seek(0)
        files = {"file": (uploaded_file.name, uploaded_file.read(), "application/pdf")}
        response = requests.post(f"{API_BASE_URL}/extract", files=files, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}


def api_decode_vin(vin: str) -> Dict[str, Any]:
    """Decode VIN via FastAPI /vin/{vin} endpoint."""
    try:
        vin = vin.strip().upper()
        response = requests.get(f"{API_BASE_URL}/vin/{vin}", timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "found":
            return {
                "status": "found",
                "summary": data.get("summary", {})
            }
        elif data.get("status") == "invalid":
            return {
                "status": "invalid",
                "message": data.get("message", "Invalid VIN")
            }
        else:
            return data
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"VIN lookup failed: {str(e)}"}


def api_summarize_contract(extracted: Dict[str, Any]) -> Dict[str, Any]:
    """Get summary, fairness score, and negotiation tips via FastAPI /summarize endpoint."""
    try:
        payload = {
            "raw_text": extracted.get("raw_text", ""),
            "llm_structured_data_full": (
                extracted.get("llm_structured_data_full") 
                or extracted.get("llm_structured_data") 
                or {}
            )
        }
        response = requests.post(f"{API_BASE_URL}/summarize", json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        return {
            "plain_summary": data.get("summary", {}).get("plain_summary", ""),
            "red_flags": data.get("summary", {}).get("red_flags", []),
            "key_terms": data.get("summary", {}).get("key_terms", []),
            "fairness_score": data.get("fairness_score", 0),
            "score_reasons": data.get("score_reasons", []),
            "negotiation_tips": data.get("negotiation_tips", {})
        }
    except requests.exceptions.RequestException as e:
        return {
            "plain_summary": f"Summary generation failed: {str(e)}",
            "red_flags": [],
            "key_terms": [],
            "fairness_score": 0,
            "score_reasons": [],
            "negotiation_tips": {}
        }


def api_chat(raw_text: str, extracted_fields: Dict[str, Any], question: str) -> str:
    """Chat with contract via FastAPI /chat endpoint."""
    try:
        payload = {
            "raw_text": raw_text,
            "extracted_fields": extracted_fields,
            "question": question
        }
        response = requests.post(f"{API_BASE_URL}/chat", json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("answer", "No answer available")
    except requests.exceptions.RequestException as e:
        return f"Chat request failed: {str(e)}"


def api_generate_negotiation_pdf(
    summary: Dict[str, Any],
    fairness_score: int,
    score_reasons: list,
    negotiation_tips: Dict[str, Any],
    structured_data: Dict[str, Any]
) -> bytes:
    """Generate negotiation PDF via FastAPI /negotiation_pdf endpoint."""
    try:
        payload = {
            "summary": summary,
            "fairness_score": fairness_score,
            "score_reasons": score_reasons,
            "negotiation_tips": negotiation_tips,
            "structured_data": structured_data
        }
        response = requests.post(f"{API_BASE_URL}/negotiation_pdf", json=payload, timeout=60)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"PDF generation failed: {str(e)}")


def api_compare_contracts(contract_a: Dict[str, Any], contract_b: Dict[str, Any]) -> Dict[str, Any]:
    """Compare two contracts via FastAPI /compare_offers endpoint."""
    try:
        # Extract structured data from both contracts
        structured_a = (
            contract_a.get("llm_structured_data_full") 
            or contract_a.get("llm_structured_data") 
            or contract_a
        )
        structured_b = (
            contract_b.get("llm_structured_data_full") 
            or contract_b.get("llm_structured_data") 
            or contract_b
        )
        
        payload = {
            "offer_a": structured_a,
            "offer_b": structured_b
        }
        response = requests.post(f"{API_BASE_URL}/compare_offers", json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Comparison failed: {str(e)}"}


def parse_money(value: str) -> float:
    """Parse money string to float."""
    if not value or value in ("", "N/A", None):
        return 0.0
    try:
        # Remove $, commas, and whitespace
        cleaned = str(value).replace("$", "").replace(",", "").strip()
        return float(cleaned)
    except:
        return 0.0


def calculate_financial_summary(structured: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate financial summary from extracted contract data."""
    core = structured.get("core", {})
    financial = structured.get("financial_analysis", {})
    
    # Extract values
    vehicle_price = parse_money(
        financial.get("vehicle_price", "") or 
        core.get("vehicle_price", "") or 
        core.get("msrp", "")
    )
    
    monthly_payment = parse_money(core.get("monthly_payment", ""))
    term_months = 0
    try:
        term_str = str(core.get("term_months", "")).strip()
        if term_str:
            term_months = int(float(term_str))
    except:
        pass
    
    down_payment = parse_money(core.get("down_payment", ""))
    
    # Calculate total amount paid
    # Formula: (Monthly Payment × Term Months) + Down Payment
    total_payments = monthly_payment * term_months if monthly_payment > 0 and term_months > 0 else 0
    total_amount_paid = total_payments + down_payment
    
    # Calculate interest paid
    # Formula: Total Paid - Principal (Vehicle Price - Down Payment)
    principal = vehicle_price - down_payment if vehicle_price > 0 else 0
    interest_paid = total_amount_paid - principal if principal > 0 else 0
    
    # Calculate total cost (interest + fees)
    # This represents the "extra" money paid beyond the vehicle price
    
    # Calculate total fees
    total_fees = 0
    doc_fee = parse_money(core.get("documentation_fee", ""))
    acq_fee = parse_money(core.get("acquisition_fee", ""))
    other_fees = core.get("other_fees", [])
    
    total_fees += doc_fee + acq_fee
    
    # Parse other fees
    for fee_str in other_fees:
        if isinstance(fee_str, str):
            # Handle list format like "['90', '425']"
            if "[" in fee_str:
                numbers = re.findall(r'\d+', fee_str)
                for num in numbers:
                    total_fees += float(num)
            else:
                total_fees += parse_money(fee_str)
        elif isinstance(fee_str, (int, float)):
            total_fees += float(fee_str)
    
    return {
        "vehicle_price": vehicle_price,
        "monthly_payment": monthly_payment,
        "term_months": term_months,
        "down_payment": down_payment,
        "total_payments": total_payments,
        "total_amount_paid": total_amount_paid,
        "interest_paid": interest_paid,
        "total_fees": total_fees,
        "principal": principal
    }

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Contract AI Analyzer",
    page_icon="Adi",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================== CUSTOM CSS STYLES ===========
st.markdown("""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Global Styles */
* {
    font-family: 'Inter', sans-serif;
    box-sizing: border-box;
}

/* Main Container */
.main .block-container {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ===================== */
/* DARK BACKGROUND */
/* ===================== */
.stApp {
    background: #020617; /* pure dark background */
    color: #e5e7eb;
}

/* ===================== */
/* HEADER */
/* ===================== */
.main-header {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
    padding: 3.5rem 2rem;
    border-radius: 0 0 32px 32px;
    margin: -2rem -1rem 3rem -1rem;
    box-shadow: 0 20px 60px rgba(99, 102, 241, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.1);
    position: relative;
    overflow: hidden;
}

.main-header::before {
    content: "";
    position: absolute;
    top: -50%;
    right: -10%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

.main-header::after {
    content: "";
    position: absolute;
    bottom: -30%;
    left: -5%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(139, 92, 246, 0.2) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

.header-content {
    position: relative;
    z-index: 1;
    max-width: 1200px;
    margin: 0 auto;
}

.main-title {
    font-size: 3.25rem;
    font-weight: 900;
    color: #ffffff;
    margin: 0 0 0.75rem 0;
    text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.main-title::before {
    content: " ";
    font-size: 3.5rem;
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

.subtitle {
    font-size: 1.2rem;
    color: rgba(255, 255, 255, 0.95);
    font-weight: 400;
    line-height: 1.6;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    max-width: 800px;
}

/* ===================== */
/* CARDS */
/* ===================== */
.custom-card {
    background: #0f172a;
    color: #e5e7eb;
    border-radius: 20px;
    padding: 2rem;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 2rem;
}

.custom-card:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.6);
}

/* Card header */
.card-header {
    font-size: 1.5rem;
    font-weight: 700;
    color: #f9fafb;
    margin-bottom: 1.5rem;
    border-bottom: 2px solid #1f2937;
    padding-bottom: 1rem;
}

/* ===================== */
/* DIVIDERS */
/* ===================== */
.section-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, #1f2937, transparent);
    margin: 3rem 0;
}

/* ===================== */
/* METRICS */
/* ===================== */
.metric-card {
    background: #020617;
    color: #e5e7eb;
    padding: 1.75rem;
    border-radius: 16px;
    text-align: center;
    border: 1px solid #1f2937;
}

.metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #f9fafb;
}

.metric-label {
    font-size: 0.875rem;
    color: #9ca3af;
    text-transform: uppercase;
    font-weight: 600;
}

/* ===================== */
/* BUTTONS */
/* ===================== */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    border-radius: 12px;
    font-weight: 600;
    border: none;
}

/* ===================== */
/* INPUTS */
/* ===================== */
.stTextInput input,
.stTextArea textarea {
    background: #020617;
    color: #e5e7eb;
    border: 2px solid #1f2937;
    border-radius: 12px;
}

.stTextInput input::placeholder {
    color: #9ca3af;
}

/* Chatbot input specific styling */
.chatbot-input-bar .stTextInput > div > div > input {
    background: transparent !important;
    border: none !important;
    color: #ffffff !important;
    font-size: 1rem !important;
    padding: 0.5rem 0 !important;
    box-shadow: none !important;
}

.chatbot-input-bar .stTextInput > div > div > input::placeholder {
    color: #9ca3af !important;
}

.chatbot-input-bar .stTextInput {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* ===================== */
/* CHAT */
/* ===================== */
.chat-container {
    background: #020617;
    border-radius: 20px;
    padding: 2rem;
    border: 1px solid #1f2937;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.55rem 0.9rem;
    border-radius: 999px;
    font-weight: 600;
    font-size: 0.9rem;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(255,255,255,0.05);
}

.status-connected { color: #22c55e; }
.status-disconnected { color: #f87171; }

.voice-tip {
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.35);
    border-radius: 12px;
    padding: 0.75rem 1rem;
    color: #c7d2fe;
}

/* ===================== */
/* CHATBOT STYLING */
/* ===================== */
[data-testid="stChatMessage"] {
    background: transparent !important;
}

.stChatMessage {
    background: transparent !important;
}

/* Custom scrollbar for chat */
div[style*="overflow-y: auto"]::-webkit-scrollbar {
    width: 8px;
}

div[style*="overflow-y: auto"]::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
}

div[style*="overflow-y: auto"]::-webkit-scrollbar-thumb {
    background: rgba(99, 102, 241, 0.5);
    border-radius: 10px;
}

div[style*="overflow-y: auto"]::-webkit-scrollbar-thumb:hover {
    background: rgba(99, 102, 241, 0.7);
}

/* ===================== */
/* CHATBOT INPUT BAR */
/* ===================== */
.chatbot-input-container {
    position: relative;
    width: 100%;
    margin: 2rem 0;
}

.chatbot-prompt {
    text-align: center;
    color: #ffffff;
    font-size: 1.5rem;
    font-weight: 500;
    margin-bottom: 1.5rem;
    letter-spacing: -0.01em;
}

.chatbot-input-bar {
    background: #1f2937;
    border-radius: 24px;
    padding: 1rem 1.25rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    position: relative;
}

.chatbot-input-bar input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: #ffffff;
    font-size: 1rem;
    padding: 0.5rem 0;
}

.chatbot-input-bar input::placeholder {
    color: #9ca3af;
}

.chatbot-icon {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    cursor: pointer;
    font-size: 1.25rem;
    user-select: none;
}

.chatbot-icon:hover {
    opacity: 0.8;
}

/* Sound Wave Animation */
.sound-wave {
    display: flex;
    align-items: center;
    gap: 3px;
    height: 24px;
}

.sound-wave-bar {
    width: 3px;
    background: #ffffff;
    border-radius: 2px;
    animation: soundWave 1.2s ease-in-out infinite;
}

.sound-wave-bar:nth-child(1) { animation-delay: 0s; height: 8px; }
.sound-wave-bar:nth-child(2) { animation-delay: 0.1s; height: 16px; }
.sound-wave-bar:nth-child(3) { animation-delay: 0.2s; height: 20px; }
.sound-wave-bar:nth-child(4) { animation-delay: 0.3s; height: 16px; }
.sound-wave-bar:nth-child(5) { animation-delay: 0.4s; height: 12px; }

@keyframes soundWave {
    0%, 100% {
        transform: scaleY(0.3);
        opacity: 0.7;
    }
    50% {
        transform: scaleY(1);
        opacity: 1;
    }
}

.sound-wave.recording .sound-wave-bar {
    animation-duration: 0.6s;
}

/* Voice button */
.voice-button {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border: none;
    transition: all 0.2s;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.voice-button:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.voice-button.recording {
    background: #ef4444;
    animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% {
        box-shadow: 0 2px 8px rgba(239, 68, 68, 0.4);
    }
    50% {
        box-shadow: 0 2px 20px rgba(239, 68, 68, 0.8);
    }
}

.voice-button svg {
    width: 20px;
    height: 20px;
    fill: #1f2937;
}

.voice-button.recording svg {
    fill: #ffffff;
}

.detail-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1.25rem;
    margin-bottom: 1.5rem;
}

.detail-pill {
    background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(17,24,39,0.95));
    border: 1px solid rgba(99,102,241,0.18);
    border-radius: 18px;
    padding: 1.1rem 1.25rem;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02);
}

.detail-label {
    font-size: 0.75rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #94a3b8;
    font-weight: 600;
    margin-bottom: 0.45rem;
}

.detail-value {
    font-size: 1.05rem;
    color: #f8fafc;
    font-weight: 600;
}

.finance-card {
    text-align: center;
    padding: 1.75rem 1.25rem;
    background: #0b1220;
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 20px;
    color: #f5f7ff;
    position: relative;
    overflow: hidden;
}

.finance-card::after {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.02);
    pointer-events: none;
}

.finance-label {
    font-size: 0.8rem;
    color: #94a3b8;
    margin-bottom: 0.5rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.finance-value {
    font-size: 2.1rem;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 0.35rem;
}

.finance-note {
    font-size: 0.8rem;
    color: #a5b4fc;
}

/* ===================== */
/* DATAFRAME */
/* ===================== */
[data-testid="stDataFrame"] {
    background: #020617;
    color: #e5e7eb;
    border: 1px solid #1f2937;
}

/* ===================== */
/* JSON */
/* ===================== */
.stJson {
    background: #020617;
    color: #e5e7eb;
    border: 1px solid #1f2937;
}

/* ===================== */
/* STATUS MESSAGES */
/* ===================== */
.stSuccess {
    background: rgba(16,185,129,0.15);
    border-left: 4px solid #10b981;
}

.stError {
    background: rgba(239,68,68,0.15);
    border-left: 4px solid #ef4444;
}

.stInfo {
    background: rgba(59,130,246,0.15);
    border-left: 4px solid #3b82f6;
}

/* ===================== */
/* SCROLLBAR */
/* ===================== */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: #020617;
}

::-webkit-scrollbar-thumb {
    background: #1f2937;
    border-radius: 10px;
}

/* ===================== */
/* FOOTER */
/* ===================== */
.footer {
    text-align: center;
    padding: 3rem;
    color: #9ca3af;
}

/* ===================== */
/* EXPANDERS */
/* ===================== */
.streamlit-expanderHeader {
    background: #ffffff !important;
    color: #1a1a1a !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    font-weight: 600 !important;
}

.streamlit-expanderContent {
    background: #ffffff !important;
    color: #1a1a1a !important;
    border: 1px solid #e5e7eb !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px !important;
    padding: 1rem !important;
}

[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
}

[data-testid="stExpander"] > div {
    background: #ffffff !important;
    color: #1a1a1a !important;
}

[data-testid="stExpander"] p,
[data-testid="stExpander"] div,
[data-testid="stExpander"] span {
    color: #1a1a1a !important;
}

/* ===================== */
/* RESPONSIVE */
/* ===================== */
@media (max-width: 768px) {
    .main-header {
        padding: 2.5rem 1.5rem;
        margin: -2rem -1rem 2rem -1rem;
    }
    
    .main-title {
        font-size: 2.25rem;
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }
    
    .main-title::before {
        font-size: 2.5rem;
    }
    
    .subtitle {
        font-size: 1rem;
    }
    
    .header-content {
        padding: 0;
    }
}
</style>
""", unsafe_allow_html=True)

# ================== SESSION STATE ==================
defaults = {
    "extracted": None,
    "extracted_contract_a": None,
    "extracted_contract_b": None,
    "comparison_result": None,
    "summary": None,
    "fairness": None,
    "reasons": None,
    "negotiation": None,
    "chat_history": [],
    "voice_transcript": "",
    "chat_input_value": "",
    "clear_chat_input": False
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ================== HEADER ==================
st.markdown("""
<div class="main-header">
    <div class="header-content">
        <h1 class="main-title">Contract AI Analyzer</h1>
        <p class="subtitle">Intelligent contract analysis powered by AI • Extract, analyze, and negotiate better deals</p>
    </div>
</div>
""", unsafe_allow_html=True)

# API Connection Status
api_connected = check_api_connection()
col1, col2 = st.columns([0.9, 0.1])

with col1:
    if api_connected:
        st.markdown('<span class="status-badge status-connected">✅ API Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge status-disconnected">❌ API Disconnected</span>', unsafe_allow_html=True)

with col2:
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ==================================================
# 📄 UPLOAD CONTRACT
# ==================================================
col_left, col_right = st.columns([0.65, 0.35])

with col_left:
    st.markdown("""
    <div class="custom-card">
        <div class="card-header"> Upload Contract PDF</div>
    """, unsafe_allow_html=True)
    
    uploaded = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload your car loan or lease contract for analysis"
    )
    
    if uploaded:
        with st.spinner("🔍 Analyzing contract with AI..."):
            try:
                st.session_state.extracted = api_extract_contract(uploaded)
                if "error" in st.session_state.extracted:
                    st.error(st.session_state.extracted["error"])
                else:
                    st.success("✅ Contract extracted successfully!")
            except Exception as e:
                st.error(f"❌ Extraction failed: {e}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.session_state.extracted:
        raw_text = st.session_state.extracted.get("raw_text", "")
        structured = (
            st.session_state.extracted.get("llm_structured_data_full")
            or st.session_state.extracted.get("llm_structured_data")
            or {}
        )
        
        st.markdown("""
        <div class="custom-card">
            <div class="card-header">🧠 Extracted Contract Data</div>
        """, unsafe_allow_html=True)
        
        # Display key fields in a nicer format
        if structured.get("core"):
            core = structured["core"]
            key_fields = ["buyer_name", "seller_name", "vin", "monthly_payment", "apr", "term_months", "vehicle_price"]
            
            # Create a grid layout
            st.markdown("<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
            
            for field in key_fields:
                if core.get(field) and core[field] not in ("", "N/A", None):
                    st.markdown(f"""
                    <div style='padding: 1.1rem; background: #0b1224; border-radius: 14px; border: 1px solid #1f2937; box-shadow: 0 6px 16px rgba(0,0,0,0.35);'>
                        <div style='font-size: 0.8rem; color: #9ca3af; text-transform: uppercase; font-weight: 700; letter-spacing: 0.03em; margin-bottom: 0.35rem;'>{field.replace('_', ' ').title()}</div>
                        <div style='font-size: 1.05rem; color: #f9fafb; font-weight: 700;'>{core[field]}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with st.expander("📋 View Full Extracted Data"):
            st.json(structured)
        
        with st.expander("📄 View Raw OCR Text"):
            st.text_area("Raw OCR Text", raw_text, height=300, label_visibility="collapsed")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # ==================================================
        # 💰 FINANCIAL SUMMARY
        # ==================================================
        financial_summary = calculate_financial_summary(structured)
        
        if financial_summary["vehicle_price"] > 0 or financial_summary["monthly_payment"] > 0:
            st.markdown("""
            <div class="custom-card" style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border: 1px solid rgba(99, 102, 241, 0.2);">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 2rem;">
                    <div style="font-size: 2rem;">💰</div>
                    <div class="card-header" style="margin: 0; border: none; padding: 0;">Financial Summary</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Show data sources
            core = structured.get("core", {})
            financial = structured.get("financial_analysis", {})
            
            # Data sources with modern dark theme
            st.markdown("""
            <div style='padding: 1.25rem 1.5rem; background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(99, 102, 241, 0.1) 100%); 
                        border-radius: 16px; border: 1px solid rgba(99, 102, 241, 0.3); margin-bottom: 2rem; 
                        backdrop-filter: blur(10px);'>
                <div style='display: flex; align-items: center; gap: 0.5rem; font-weight: 600; color: #93c5fd; margin-bottom: 1rem; font-size: 0.95rem;'>
                    <span style='font-size: 1.1rem;'> </span>
                    <span>Data Sources</span>
                </div>
            """, unsafe_allow_html=True)
            
            source_info = []
            if financial.get("vehicle_price") or core.get("vehicle_price") or core.get("msrp"):
                source_info.append("Vehicle Price: Extracted from contract")
            if core.get("monthly_payment"):
                source_info.append("Monthly Payment: Extracted from contract")
            if core.get("term_months"):
                source_info.append("Term: Extracted from contract")
            if core.get("down_payment"):
                source_info.append("Down Payment: Extracted from contract")
            
            for info in source_info:
                st.markdown(f"<div style='font-size: 0.85rem; color: #cbd5e1; margin: 0.4rem 0; padding-left: 0.5rem;'>• {info}</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Modern financial cards with gradients and better styling
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div style="text-align: center; padding: 2rem 1.5rem; 
                            background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
                            border: 1px solid rgba(255, 255, 255, 0.1); 
                            border-radius: 20px; 
                            transition: all 0.3s ease;
                            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                            position: relative;
                            overflow: hidden;">
                    <div style="position: absolute; top: 0; right: 0; width: 60px; height: 60px; 
                                background: radial-gradient(circle, rgba(99, 102, 241, 0.2) 0%, transparent 70%);
                                border-radius: 0 20px 0 100px;"></div>
                    <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 1rem; font-weight: 700; 
                                text-transform: uppercase; letter-spacing: 0.1em;">VEHICLE PRICE</div>
                    <div style="font-size: 2.25rem; font-weight: 800; color: #f8fafc; margin-bottom: 0.75rem; 
                                text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);">${financial_summary['vehicle_price']:,.2f}</div>
                    <div style="font-size: 0.7rem; color: #64748b; margin-top: 0.5rem; font-weight: 500;">Contract extraction</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="text-align: center; padding: 2rem 1.5rem; 
                            background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
                            border: 1px solid rgba(255, 255, 255, 0.1); 
                            border-radius: 20px; 
                            transition: all 0.3s ease;
                            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                            position: relative;
                            overflow: hidden;">
                    <div style="position: absolute; top: 0; right: 0; width: 60px; height: 60px; 
                                background: radial-gradient(circle, rgba(16, 185, 129, 0.2) 0%, transparent 70%);
                                border-radius: 0 20px 0 100px;"></div>
                    <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 1rem; font-weight: 700; 
                                text-transform: uppercase; letter-spacing: 0.1em;">MONTHLY PAYMENT</div>
                    <div style="font-size: 2.25rem; font-weight: 800; color: #f8fafc; margin-bottom: 0.75rem; 
                                text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);">${financial_summary['monthly_payment']:,.2f}</div>
                    <div style="font-size: 0.75rem; color: #10b981; margin-top: 0.5rem; font-weight: 600;">{financial_summary['term_months']} months</div>
                    <div style="font-size: 0.7rem; color: #64748b; margin-top: 0.25rem; font-weight: 500;">Contract extraction</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                calculation = f"${financial_summary['monthly_payment']:,.2f} × {financial_summary['term_months']}"
                if financial_summary['down_payment'] > 0:
                    calculation += f"<br>+ ${financial_summary['down_payment']:,.2f} down"
                
                st.markdown(f"""
                <div style="text-align: center; padding: 2rem 1.5rem; 
                            background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
                            border: 1px solid rgba(255, 255, 255, 0.1); 
                            border-radius: 20px; 
                            transition: all 0.3s ease;
                            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                            position: relative;
                            overflow: hidden;">
                    <div style="position: absolute; top: 0; right: 0; width: 60px; height: 60px; 
                                background: radial-gradient(circle, rgba(245, 158, 11, 0.2) 0%, transparent 70%);
                                border-radius: 0 20px 0 100px;"></div>
                    <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 1rem; font-weight: 700; 
                                text-transform: uppercase; letter-spacing: 0.1em;">TOTAL AMOUNT PAID</div>
                    <div style="font-size: 2.25rem; font-weight: 800; color: #f8fafc; margin-bottom: 0.75rem; 
                                text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);">${financial_summary['total_amount_paid']:,.2f}</div>
                    <div style="font-size: 0.7rem; color: #64748b; margin-top: 0.5rem; line-height: 1.5; font-weight: 500;">{calculation}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                total_cost = financial_summary['interest_paid'] + financial_summary['total_fees']
                if total_cost < 0:
                    total_cost = 0
                
                st.markdown(f"""
                <div style="text-align: center; padding: 2rem 1.5rem; 
                            background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
                            border: 1px solid rgba(255, 255, 255, 0.1); 
                            border-radius: 20px; 
                            transition: all 0.3s ease;
                            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                            position: relative;
                            overflow: hidden;">
                    <div style="position: absolute; top: 0; right: 0; width: 60px; height: 60px; 
                                background: radial-gradient(circle, rgba(239, 68, 68, 0.2) 0%, transparent 70%);
                                border-radius: 0 20px 0 100px;"></div>
                    <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 1rem; font-weight: 700; 
                                text-transform: uppercase; letter-spacing: 0.1em;">TOTAL COST</div>
                    <div style="font-size: 2.25rem; font-weight: 800; color: #f8fafc; margin-bottom: 0.75rem; 
                                text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);">${total_cost:,.2f}</div>
                    <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.5rem; font-weight: 500;">Interest + Fees</div>
                    <div style="font-size: 0.7rem; color: #64748b; margin-top: 0.25rem; font-weight: 500;">vs Vehicle Price</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Calculation Details section with modern styling
            st.markdown("<div style='margin-top: 3rem; padding-top: 2.5rem; border-top: 1px solid rgba(255, 255, 255, 0.1);'>", unsafe_allow_html=True)
            st.markdown("""
            <div style='display: flex; align-items: center; gap: 0.75rem; font-weight: 700; color: #f8fafc; margin-bottom: 2rem; font-size: 1.25rem;'>
                <span style='font-size: 1.5rem;'>📐</span>
                <span>Calculation Details</span>
            </div>
            """, unsafe_allow_html=True)
            
            breakdown_col1, breakdown_col2, breakdown_col3 = st.columns(3)
            
            with breakdown_col1:
                principal = financial_summary['vehicle_price'] - financial_summary['down_payment']
                interest_calc = f"${financial_summary['total_amount_paid']:,.2f} - ${principal:,.2f}"
                if financial_summary['interest_paid'] < 0:
                    interest_calc = "Check data"
                
                st.markdown(f"""
                <div style="padding: 2rem 1.75rem; 
                            background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(99, 102, 241, 0.1) 100%);
                            border: 1px solid rgba(99, 102, 241, 0.3); 
                            border-radius: 20px; 
                            border-left: 4px solid #6366f1;
                            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
                            position: relative;
                            overflow: hidden;">
                    <div style="position: absolute; top: -20px; right: -20px; width: 80px; height: 80px; 
                                background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 70%);
                                border-radius: 50%;"></div>
                    <div style="font-weight: 700; color: #93c5fd; margin-bottom: 1rem; font-size: 0.85rem; 
                                text-transform: uppercase; letter-spacing: 0.1em;">INTEREST PAID</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #f8fafc; margin-bottom: 1rem; 
                                text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);">${max(0, financial_summary['interest_paid']):,.2f}</div>
                    <div style="font-size: 0.8rem; color: #cbd5e1; line-height: 1.6; font-weight: 500;">{interest_calc}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with breakdown_col2:
                fees_breakdown = []
                if financial_summary['total_fees'] > 0:
                    doc_fee = parse_money(core.get("documentation_fee", ""))
                    acq_fee = parse_money(core.get("acquisition_fee", ""))
                    other_fees = core.get("other_fees", [])
                    other_total = financial_summary['total_fees'] - doc_fee - acq_fee
                    
                    if doc_fee > 0:
                        fees_breakdown.append(f"Doc: ${doc_fee:,.2f}")
                    if acq_fee > 0:
                        fees_breakdown.append(f"Acq: ${acq_fee:,.2f}")
                    if other_total > 0:
                        fees_breakdown.append(f"Other: ${other_total:,.2f}")
                
                fees_text = " + ".join(fees_breakdown) if fees_breakdown else "No fees"
                
                st.markdown(f"""
                <div style="padding: 2rem 1.75rem; 
                            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.1) 100%);
                            border: 1px solid rgba(16, 185, 129, 0.3); 
                            border-radius: 20px; 
                            border-left: 4px solid #10b981;
                            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
                            position: relative;
                            overflow: hidden;">
                    <div style="position: absolute; top: -20px; right: -20px; width: 80px; height: 80px; 
                                background: radial-gradient(circle, rgba(16, 185, 129, 0.1) 0%, transparent 70%);
                                border-radius: 50%;"></div>
                    <div style="font-weight: 700; color: #6ee7b7; margin-bottom: 1rem; font-size: 0.85rem; 
                                text-transform: uppercase; letter-spacing: 0.1em;">TOTAL FEES</div>
                    <div style="font-size: 2rem; font-weight: 800; color: #f8fafc; margin-bottom: 1rem; 
                                text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);">${financial_summary['total_fees']:,.2f}</div>
                    <div style="font-size: 0.8rem; color: #cbd5e1; line-height: 1.6; font-weight: 500;">{fees_text}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with breakdown_col3:
                if financial_summary['down_payment'] > 0:
                    st.markdown(f"""
                    <div style="padding: 2rem 1.75rem; 
                                background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(124, 58, 237, 0.1) 100%);
                                border: 1px solid rgba(139, 92, 246, 0.3); 
                                border-radius: 20px; 
                                border-left: 4px solid #8b5cf6;
                                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
                                position: relative;
                                overflow: hidden;">
                        <div style="position: absolute; top: -20px; right: -20px; width: 80px; height: 80px; 
                                    background: radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%);
                                    border-radius: 50%;"></div>
                        <div style="font-weight: 700; color: #c4b5fd; margin-bottom: 1rem; font-size: 0.85rem; 
                                    text-transform: uppercase; letter-spacing: 0.1em;">DOWN PAYMENT</div>
                        <div style="font-size: 2rem; font-weight: 800; color: #f8fafc; margin-bottom: 1rem; 
                                    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);">${financial_summary['down_payment']:,.2f}</div>
                        <div style="font-size: 0.8rem; color: #cbd5e1; font-weight: 500;">Contract extraction</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="padding: 2rem 1.75rem; 
                                background: linear-gradient(135deg, rgba(148, 163, 184, 0.15) 0%, rgba(100, 116, 139, 0.1) 100%);
                                border: 1px solid rgba(148, 163, 184, 0.3); 
                                border-radius: 20px; 
                                border-left: 4px solid #94a3b8;
                                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
                                position: relative;
                                overflow: hidden;">
                        <div style="position: absolute; top: -20px; right: -20px; width: 80px; height: 80px; 
                                    background: radial-gradient(circle, rgba(148, 163, 184, 0.1) 0%, transparent 70%);
                                    border-radius: 50%;"></div>
                        <div style="font-weight: 700; color: #cbd5e1; margin-bottom: 1rem; font-size: 0.85rem; 
                                    text-transform: uppercase; letter-spacing: 0.1em;">DOWN PAYMENT</div>
                        <div style="font-size: 2rem; font-weight: 800; color: #64748b; margin-bottom: 1rem;">$0.00</div>
                        <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 500;">Not found</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

# ==================================================
# 🔍 VIN LOOKUP
# ==================================================
with col_right:
    st.markdown("""
    <div class="custom-card">
        <div class="card-header">🔍 VIN Lookup</div>
    """, unsafe_allow_html=True)
    
    vin = st.text_input(
        "Enter Vehicle Identification Number",
        placeholder="17 characters",
        help="Enter a 17-character VIN to get vehicle details"
    )
    
    if st.button("🔎 Search VIN", use_container_width=True):
        if len(vin.strip()) != 17:
            st.error("⚠️ VIN must be exactly 17 characters")
        else:
            with st.spinner("🔍 Decoding VIN..."):
                vin_data = api_decode_vin(vin.strip())
                
                if vin_data.get("status") == "found":
                    st.success("✅ VIN Found")
                    summary = vin_data.get("summary", {})
                    
                    # Display key info nicely
                    if summary.get("year") and summary.get("make") and summary.get("model"):
                        st.markdown(f"### {summary.get('year')} {summary.get('make')} {summary.get('model')}")
                    
                    with st.expander(" View Full Details"):
                        st.json(summary)
                elif vin_data.get("status") == "invalid":
                    st.error(f"❌ {vin_data.get('message', 'Invalid VIN')}")
                else:
                    st.error(f"❌ {vin_data.get('message', 'VIN lookup failed')}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==================================================
# 📊 SUMMARY & FAIRNESS
# ==================================================
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

if st.session_state.extracted:
    col_btn, _ = st.columns([0.3, 0.7])
    with col_btn:
        if st.button(" Generate Analysis", use_container_width=True, type="primary"):
            with st.spinner(" AI is analyzing your contract..."):
                result = api_summarize_contract(st.session_state.extracted)
                st.session_state.summary = {
                    "plain_summary": result.get("plain_summary", ""),
                    "red_flags": result.get("red_flags", []),
                    "key_terms": result.get("key_terms", [])
                }
                st.session_state.fairness = result.get("fairness_score", 0)
                st.session_state.reasons = result.get("score_reasons", [])
                st.session_state.negotiation = result.get("negotiation_tips", {})
            st.success("✅ Analysis complete!")

if st.session_state.summary:
    # Fairness Score Card
    score = st.session_state.fairness
    score_color = "#10b981" if score >= 70 else "#f59e0b" if score >= 50 else "#ef4444"
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("""
        <div class="custom-card">
            <div class="card-header"> Contract Summary</div>
        """, unsafe_allow_html=True)
        summary_text = st.session_state.summary.get("plain_summary", "—")
        st.markdown(f"<div style='line-height: 1.8; color: #e5e7eb; font-size: 1rem;'>{summary_text}</div>", unsafe_allow_html=True)
        
        # Key Terms
        key_terms = st.session_state.summary.get("key_terms", [])
        if key_terms:
            st.markdown("<div style='margin-top: 1.5rem; padding-top: 1.5rem; border-top: 2px solid #f0f0f0;'>", unsafe_allow_html=True)
            st.markdown("**🔑 Key Terms:**", unsafe_allow_html=True)
            st.markdown("<div style='margin-top: 0.75rem;'>", unsafe_allow_html=True)
            for term in key_terms:
                st.markdown(f"<div style='padding: 0.6rem 0; color: #f8fafc; font-size: 0.95rem;'>• {term}</div>", unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="custom-card">
            <div class="card-header">⚠️ Red Flags</div>
        """, unsafe_allow_html=True)
        flags = st.session_state.summary.get("red_flags", [])
        if flags:
            st.markdown("<div style='display: flex; flex-direction: column; gap: 0.75rem;'>", unsafe_allow_html=True)
            for f in flags:
                st.markdown(f"""
                <div style='padding: 0.875rem; background: #fee2e2; border-left: 4px solid #ef4444; border-radius: 8px; color: #991b1b; font-size: 0.9rem;'>
                    🔴 {f}
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='padding: 1.5rem; text-align: center; background: #d1fae5; border-radius: 12px; color: #065f46; font-weight: 600;'>
                ✅ None found
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="padding: 2rem; background: #ffffff; border: 3px solid {score_color}; border-radius: 20px; text-align: center; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);">
            <div style="font-size: 0.85rem; color: #6b7280; margin-bottom: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Fairness Score</div>
            <div style="font-size: 3rem; font-weight: 800; color: {score_color}; margin: 0.5rem 0;">{score}</div>
            <div style="font-size: 1rem; color: #6b7280; font-weight: 500;">out of 100</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #ffffff; border-radius: 20px; padding: 2rem; border: 1px solid rgba(255,255,255,0.08); margin-bottom: 1.5rem;">
            <div style="font-size: 1.5rem; font-weight: 700; color: #1a1a1a; margin-bottom: 1.5rem; border-bottom: 2px solid #e5e7eb; padding-bottom: 1rem;">📊 Score Details</div>
        """, unsafe_allow_html=True)
        reasons = st.session_state.reasons[:5] or []
        if reasons:
            st.markdown("<div style='display: flex; flex-direction: column; gap: 0.75rem;'>", unsafe_allow_html=True)
            for r in reasons:
                st.markdown(f"<div style='padding: 0.875rem 1rem; background: #f9fafb; border-left: 4px solid #6366f1; border-radius: 8px; color: #1a1a1a; font-size: 0.9rem; line-height: 1.6;'>• {r}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==================================================
# ✏️ NEGOTIATION
# ==================================================
if st.session_state.negotiation:
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="custom-card">
        <div class="card-header"> Negotiation Messages</div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["💬 Polite", "💼 Firm", "⚖️ Legal-Based"])
    
    with tab1:
        polite = st.text_area(
            "Polite Message",
            st.session_state.negotiation.get("polite", ""),
            height=150,
            label_visibility="collapsed"
        )
    
    with tab2:
        firm = st.text_area(
            "Firm Message",
            st.session_state.negotiation.get("firm", ""),
            height=150,
            label_visibility="collapsed"
        )
    
    with tab3:
        legal = st.text_area(
            "Legal-Based Message",
            st.session_state.negotiation.get("legal_based", ""),
            height=150,
            label_visibility="collapsed"
        )
    
    if st.button(" Download Negotiation PDF", use_container_width=True):
        with st.spinner(" Generating PDF..."):
            try:
                structured_data = (
                    st.session_state.extracted.get("llm_structured_data_full")
                    or st.session_state.extracted.get("llm_structured_data")
                    or {}
                )
                pdf_bytes = api_generate_negotiation_pdf(
                    summary=st.session_state.summary,
                    fairness_score=st.session_state.fairness,
                    score_reasons=st.session_state.reasons,
                    negotiation_tips={
                        "polite": polite,
                        "firm": firm,
                        "legal_based": legal
                    },
                    structured_data=structured_data
                )
                st.download_button(
                    "⬇️ Download PDF Report",
                    pdf_bytes,
                    "negotiation_report.pdf",
                    "application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ PDF generation failed: {e}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ================== VOICE FUNCTIONS ==================
def text_to_speech(text: str) -> str:
    """Convert text to speech and return base64 audio."""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        audio_base64 = base64.b64encode(audio_buffer.read()).decode()
        return audio_base64
    except Exception as e:
        st.error(f"Voice synthesis error: {e}")
        return None

def _clear_chat_inputs():
    """Reset mic transcript and text input without touching other state."""
    st.session_state.voice_transcript = ""
    st.session_state.chat_question_input = ""
    if "last_audio" in st.session_state:
        del st.session_state.last_audio

# ==================================================
# 💬 CHATBOT
# ==================================================
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

st.markdown("""
<div style="margin-bottom: 2rem;">
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
        <div style="font-size: 2rem;"></div>
        <div style="font-size: 1.5rem; font-weight: 700; color: #f8fafc;">Ask About Your Contract</div>
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.extracted:
    # Initialize session state
    if "chat_question_input" not in st.session_state:
        st.session_state.chat_question_input = ""
    if "voice_enabled" not in st.session_state:
        st.session_state.voice_enabled = True
    if "is_voice_recording" not in st.session_state:
        st.session_state.is_voice_recording = False
    
    # Custom input box with voice button using HTML
    st.markdown("""
    <style>
    .chat-input-container {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        background: #1a1a1a;
        border: 2px solid #444;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .chat-input-container:focus-within {
        border-color: #6366f1;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    
    .chat-input-container input {
        flex: 1;
        background: transparent;
        border: none;
        outline: none;
        color: #fff;
        font-size: 0.95rem;
    }
    
    .chat-input-container input::placeholder {
        color: #888;
    }
    
    .chat-bubble-btn {
        background: #6366f1;
        border: none;
        cursor: pointer;
        font-size: 1.3rem;
        padding: 0.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
        border-radius: 8px;
        flex-shrink: 0;
        width: 36px;
        height: 36px;
        box-shadow: 0 2px 6px rgba(99, 102, 241, 0.3);
    }
    
    .chat-bubble-btn:hover {
        background: #7c3aed;
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.5);
    }
    
    .chat-bubble-btn.recording {
        background: #ef4444;
        animation: pulse-recording 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse-recording {
        0%, 100% {
            box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
        }
        50% {
            box-shadow: 0 0 0 8px rgba(239, 68, 68, 0);
        }
    }
    
    .voice-status {
        font-size: 0.8rem;
        color: #888;
        text-align: center;
        margin-top: 0.5rem;
        height: 16px;
    }
    
    .voice-status.recording {
        color: #ef4444;
        font-weight: bold;
    }
    
    .voice-status.success {
        color: #10b981;
    }
    </style>
    
    <div style="margin-bottom: 0.5rem; font-size: 0.85rem; color: #999;">
         <strong>Tip:</strong> Click the blue button to speak your question, or type below
    </div>
    
    <div class="chat-input-container">
        <input type="text" id="voice-chat-input" placeholder="Type your question here..." />
        <button class="chat-bubble-btn" id="voice-btn-icon" type="button" title="Click and speak your question">💬</button>
    </div>
    
    <div class="voice-status" id="voice-status"></div>
    
    <script>
    const voiceChatInput = document.getElementById('voice-chat-input');
    const voiceBtnIcon = document.getElementById('voice-btn-icon');
    const voiceStatus = document.getElementById('voice-status');
    let isRecording = false;
    
    voiceBtnIcon.addEventListener('click', function(e) {
        e.preventDefault();
        
        if (!isRecording) {
            isRecording = true;
            voiceBtnIcon.classList.add('recording');
            voiceStatus.textContent = '🎙️ Listening... speak now';
            voiceStatus.classList.add('recording');
        }
        
        // Find and click the hidden Streamlit voice button
        const streamlitVoiceBtn = document.querySelector('[title="Record"]') || 
                                 document.querySelector('button[aria-label*="record"]') ||
                                 Array.from(document.querySelectorAll('button')).find(btn => 
                                     btn.innerHTML.includes('🎤') || btn.title.includes('Record')
                                 );
        if (streamlitVoiceBtn) {
            streamlitVoiceBtn.click();
        }
        
        // Reset after timeout
        setTimeout(() => {
            if (isRecording) {
                isRecording = false;
                voiceBtnIcon.classList.remove('recording');
                voiceStatus.textContent = '⏳ Processing...';
                voiceStatus.classList.remove('recording');
            }
        }, 6000);
    });
    
    // Monitor for recording completion
    const observer = setInterval(() => {
        const recordBtn = document.querySelector('button[aria-label*="stop"]') || 
                         document.querySelector('button[title*="Stop"]');
        if (!recordBtn && isRecording) {
            isRecording = false;
            voiceBtnIcon.classList.remove('recording');
            voiceStatus.textContent = '✅ Processing your question...';
            voiceStatus.classList.add('success');
        }
    }, 200);
    </script>
    """, unsafe_allow_html=True)
    
    # Hidden text input for Streamlit state management
    col_input, col_voice_btn = st.columns([0.95, 0.05])
    
    with col_input:
        question_text = st.text_input(
            "Type your question here...",
            value=st.session_state.get("chat_question_input", ""),
            placeholder="Type your question here...",
            label_visibility="collapsed",
            key="chat_input_main"
        )
    
    with col_voice_btn:
        # Voice recorder component (hidden)
        st.markdown('<div style="display: none;">', unsafe_allow_html=True)
        transcript = speech_to_text(
            language="en-US",
            start_prompt="",
            stop_prompt="",
            use_container_width=False,
            just_once=False,
            key="voice_recorder"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Update input with voice transcript
    if transcript:
        if transcript != question_text:
            st.session_state.chat_question_input = transcript
            st.rerun()
    
    # Display chat history FIRST (before processing)
    if st.session_state.chat_history:
        st.markdown("""
        <div style="background: #0f172a; border-radius: 20px; padding: 1.5rem; 
                    border: 1px solid rgba(255, 255, 255, 0.1); 
                    margin-top: 2rem; max-height: 400px; overflow-y: auto;">
        """, unsafe_allow_html=True)
        
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); 
                            color: white; padding: 0.75rem 1rem; border-radius: 18px; 
                            margin-bottom: 0.75rem; margin-left: auto; max-width: 75%; 
                            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);">
                    <div style="font-weight: 600; margin-bottom: 0.25rem; font-size: 0.9rem;">You</div>
                    <div style="line-height: 1.5; font-size: 0.95rem;">{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.05); 
                            color: #e5e7eb; padding: 0.75rem 1rem; border-radius: 18px; 
                            margin-bottom: 0.75rem; max-width: 75%; 
                            border: 1px solid rgba(255, 255, 255, 0.1);
                            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);">
                    <div style="font-weight: 600; margin-bottom: 0.25rem; color: #a5b4fc; font-size: 0.9rem;">🤖 AI Assistant</div>
                    <div style="line-height: 1.5; font-size: 0.95rem;">{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Process question when user presses Enter or input changes
    if question_text.strip() and question_text != st.session_state.get("last_processed_question", ""):
        st.session_state.last_processed_question = question_text
        question = question_text.strip()
        st.session_state.chat_history.append({"role": "user", "content": question})
        st.session_state.chat_question_input = ""
        
        with st.spinner("🤔 Getting answer..."):
            extracted_fields = (
                st.session_state.extracted.get("llm_structured_data_full")
                or st.session_state.extracted.get("llm_structured_data")
                or {}
            )
            answer = api_chat(
                raw_text=st.session_state.extracted.get("raw_text", ""),
                extracted_fields=extracted_fields,
                question=question
            )
            st.session_state.chat_history.append(
                {"role": "assistant", "content": answer}
            )
        
        # Generate voice response SEPARATELY (without blocking UI)
        if st.session_state.get("voice_enabled", True):
            try:
                audio_base64 = text_to_speech(answer)
                if audio_base64:
                    st.session_state.last_audio = audio_base64
                    st.session_state.last_answer = answer
                    st.session_state.play_audio = True
            except Exception as e:
                pass  # Fail silently for voice generation
        
        st.rerun()
    
    # Play audio if available and voice is enabled
    if (st.session_state.get("play_audio", False) and 
        "last_audio" in st.session_state and 
        st.session_state.get("voice_enabled", True)):
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); 
                    border-radius: 12px; padding: 1rem; margin-top: 1rem;">
            <div style="color: #6ee7b7; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem;">
                🔊 Playing Response
            </div>
        """, unsafe_allow_html=True)
        st.audio(
            io.BytesIO(base64.b64decode(st.session_state.last_audio)),
            format="audio/mp3",
            autoplay=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
        st.session_state.play_audio = False
        
else:
    st.markdown("""
    <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); 
                border-radius: 16px; padding: 2rem; text-align: center;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">📄</div>
        <div style="font-size: 1.2rem; font-weight: 600; color: #93c5fd; margin-bottom: 0.5rem;">
            Upload a contract to start chatting
        </div>
        <div style="color: #94a3b8; font-size: 0.95rem;">
            Upload your contract PDF above to ask questions about your contract terms
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================================================
# 🔄 CONTRACT COMPARISON
# ==================================================
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("""
<div class="custom-card">
    <div class="card-header">🔄 Compare Two Contracts</div>
</div>
""", unsafe_allow_html=True)

st.markdown("**Upload two contracts to compare and find the best deal**", unsafe_allow_html=True)

comp_col1, comp_col2 = st.columns(2)

with comp_col1:
    st.subheader("📄 Contract A")
    uploaded_a = st.file_uploader(
        "Upload first contract (PDF)",
        type=["pdf"],
        key="contract_a",
        help="Upload the first contract to compare"
    )
    
    if uploaded_a:
        with st.spinner("🔍 Extracting Contract A..."):
            try:
                st.session_state.extracted_contract_a = api_extract_contract(uploaded_a)
                if "error" not in st.session_state.extracted_contract_a:
                    st.success("✅ Contract A extracted")
                else:
                    st.error(st.session_state.extracted_contract_a.get("error"))
            except Exception as e:
                st.error(f"❌ Failed: {e}")
    
    if st.session_state.extracted_contract_a and "error" not in st.session_state.extracted_contract_a:
        structured_a = (
            st.session_state.extracted_contract_a.get("llm_structured_data_full")
            or st.session_state.extracted_contract_a.get("llm_structured_data")
            or {}
        )
        if structured_a.get("core"):
            core_a = structured_a["core"]
            st.markdown("**Key Details:**")
            st.markdown("<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:0.75rem;'>", unsafe_allow_html=True)
            def _pill(label, value):
                return f"""
                <div style='background:#0b1224;border:1px solid #1f2937;border-radius:12px;padding:0.9rem 1rem;box-shadow:0 8px 18px rgba(0,0,0,0.35);'>
                    <div style='font-size:0.78rem;color:#9ca3af;text-transform:uppercase;font-weight:700;letter-spacing:0.04em;'>{label}</div>
                    <div style='font-size:1.05rem;color:#f9fafb;font-weight:700;margin-top:0.25rem;'>{value}</div>
                </div>
                """
            if core_a.get("monthly_payment"):
                st.markdown(_pill("Monthly Payment", core_a.get("monthly_payment")), unsafe_allow_html=True)
            if core_a.get("apr"):
                st.markdown(_pill("APR", core_a.get("apr")), unsafe_allow_html=True)
            if core_a.get("term_months"):
                st.markdown(_pill("Term", f"{core_a.get('term_months')} months"), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

with comp_col2:
    st.subheader("📄 Contract B")
    uploaded_b = st.file_uploader(
        "Upload second contract (PDF)",
        type=["pdf"],
        key="contract_b",
        help="Upload the second contract to compare"
    )
    
    if uploaded_b:
        with st.spinner("🔍 Extracting Contract B..."):
            try:
                st.session_state.extracted_contract_b = api_extract_contract(uploaded_b)
                if "error" not in st.session_state.extracted_contract_b:
                    st.success("✅ Contract B extracted")
                else:
                    st.error(st.session_state.extracted_contract_b.get("error"))
            except Exception as e:
                st.error(f"❌ Failed: {e}")
    
    if st.session_state.extracted_contract_b and "error" not in st.session_state.extracted_contract_b:
        structured_b = (
            st.session_state.extracted_contract_b.get("llm_structured_data_full")
            or st.session_state.extracted_contract_b.get("llm_structured_data")
            or {}
        )
        if structured_b.get("core"):
            core_b = structured_b["core"]
            st.markdown("**Key Details:**")
            st.markdown("<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:0.75rem;'>", unsafe_allow_html=True)
            def _pill_b(label, value):
                return f"""
                <div style='background:#0b1224;border:1px solid #1f2937;border-radius:12px;padding:0.9rem 1rem;box-shadow:0 8px 18px rgba(0,0,0,0.35);'>
                    <div style='font-size:0.78rem;color:#9ca3af;text-transform:uppercase;font-weight:700;letter-spacing:0.04em;'>{label}</div>
                    <div style='font-size:1.05rem;color:#f9fafb;font-weight:700;margin-top:0.25rem;'>{value}</div>
                </div>
                """
            if core_b.get("monthly_payment"):
                st.markdown(_pill_b("Monthly Payment", core_b.get("monthly_payment")), unsafe_allow_html=True)
            if core_b.get("apr"):
                st.markdown(_pill_b("APR", core_b.get("apr")), unsafe_allow_html=True)
            if core_b.get("term_months"):
                st.markdown(_pill_b("Term", f"{core_b.get('term_months')} months"), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# Compare button
if (st.session_state.extracted_contract_a and "error" not in st.session_state.extracted_contract_a and
    st.session_state.extracted_contract_b and "error" not in st.session_state.extracted_contract_b):
    
    if st.button("🔄 Compare Contracts", use_container_width=True, type="primary"):
        with st.spinner("🔄 Comparing contracts..."):
            comparison = api_compare_contracts(
                st.session_state.extracted_contract_a,
                st.session_state.extracted_contract_b
            )
            
            if "error" not in comparison:
                st.session_state.comparison_result = comparison
                st.success("✅ Comparison complete!")
            else:
                st.error(comparison.get("error"))

# Display comparison results
# ===============================
# 📊 Display comparison results
# ===============================
if st.session_state.comparison_result:

    comp_result = st.session_state.comparison_result

    st.markdown("""
    <div class="custom-card">
        <div class="card-header"> Comparison Results</div>
    """, unsafe_allow_html=True)

    # ✅ Extract offers FIRST
    offer_a = comp_result.get("offer_a") or {}
    offer_b = comp_result.get("offer_b") or {}

    # ✅ Extract scores safely
    score_a = int(offer_a.get("score", 0) or 0)
    score_b = int(offer_b.get("score", 0) or 0)

    # ✅ Best offer
    best = comp_result.get("best_offer", "Tie")

    # ===============================
    # 🏆 Winner announcement
    # ===============================
    if best == "A":
        st.markdown(f"""
        <div style="padding:2rem;background:linear-gradient(135deg,#d1fae5,#a7f3d0);
        border:3px solid #10b981;border-radius:20px;margin-bottom:2rem;text-align:center;">
            <div style="font-size:3rem;">🏆</div>
            <h3 style="color:#065f46;">Winner: Contract A</h3>
            <p style="color:#047857;">
                Contract A has a better fairness score ({score_a}/100 vs {score_b}/100).
            </p>
        </div>
        """, unsafe_allow_html=True)

    elif best == "B":
        st.markdown(f"""
        <div style="padding:2rem;background:linear-gradient(135deg,#d1fae5,#a7f3d0);
        border:3px solid #10b981;border-radius:20px;margin-bottom:2rem;text-align:center;">
            <div style="font-size:3rem;">🏆</div>
            <h3 style="color:#065f46;">Winner: Contract B</h3>
            <p style="color:#047857;">
                Contract B has a better fairness score ({score_b}/100 vs {score_a}/100).
            </p>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div style="padding:2rem;background:linear-gradient(135deg,#fef3c7,#fde68a);
        border:3px solid #f59e0b;border-radius:20px;margin-bottom:2rem;text-align:center;">
            <div style="font-size:3rem;">🤝</div>
            <h3 style="color:#92400e;">Tie</h3>
            <p style="color:#b45309;">
                Both contracts have similar fairness scores ({score_a}/100 vs {score_b}/100).
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ===============================
    # 📊 Side-by-side layout
    # ===============================
    comp_col_a, comp_col_b = st.columns(2)

    score_color_a = "#10b981" if score_a >= 70 else "#f59e0b" if score_a >= 50 else "#ef4444"
    score_color_b = "#10b981" if score_b >= 70 else "#f59e0b" if score_b >= 50 else "#ef4444"

    
     

    with comp_col_a:
        st.markdown(f"""
        <div style="padding: 2rem; background: #ffffff; border: 2px solid #e5e7eb; border-radius: 20px; margin-bottom: 1.5rem;">
            <h3 style="margin: 0 0 1.5rem 0; color: #1a1a1a; font-size: 1.5rem; font-weight: 700;">Contract A</h3>
            <div style="text-align: center; padding: 1.5rem; background: #f9fafb; border: 3px solid {score_color_a}; border-radius: 16px; margin-bottom: 1.5rem;">
                <div style="font-size: 0.85rem; color: #6b7280; margin-bottom: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Fairness Score</div>
                <div style="font-size: 3rem; font-weight: 800; color: {score_color_a};">{score_a}</div>
                <div style="font-size: 1rem; color: #6b7280; margin-top: 0.5rem; font-weight: 500;">out of 100</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Key fields
        fields_a = offer_a.get("fields", {}).get("core", {})
        st.markdown("<div style='color: #1a1a1a; font-weight: 700; font-size: 1.1rem; margin-bottom: 1rem;'>**Key Terms:**</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top: 0.75rem;'>", unsafe_allow_html=True)
        if fields_a.get("monthly_payment"):
            st.markdown(f"<div style='padding: 1rem; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; margin-bottom: 0.75rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'><strong style='color: #1a1a1a;'>Monthly Payment:</strong> <span style='color: #374151;'>{fields_a.get('monthly_payment')}</span></div>", unsafe_allow_html=True)
        if fields_a.get("apr"):
            st.markdown(f"<div style='padding: 1rem; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; margin-bottom: 0.75rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'><strong style='color: #1a1a1a;'>APR:</strong> <span style='color: #374151;'>{fields_a.get('apr')}</span></div>", unsafe_allow_html=True)
        if fields_a.get("term_months"):
            st.markdown(f"<div style='padding: 1rem; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; margin-bottom: 0.75rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'><strong style='color: #1a1a1a;'>Term:</strong> <span style='color: #374151;'>{fields_a.get('term_months')} months</span></div>", unsafe_allow_html=True)
        if fields_a.get("vehicle_price"):
            st.markdown(f"<div style='padding: 1rem; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; margin-bottom: 0.75rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'><strong style='color: #1a1a1a;'>Vehicle Price:</strong> <span style='color: #374151;'>{fields_a.get('vehicle_price')}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Score reasons
        reasons_a = offer_a.get("reasons", [])
        if reasons_a:
            with st.expander(" View Score Details"):
                st.markdown("<div style='display: flex; flex-direction: column; gap: 0.75rem; background: #ffffff; padding: 1rem; border-radius: 12px;'>", unsafe_allow_html=True)
                for reason in reasons_a[:5]:
                    st.markdown(f"<div style='padding: 0.875rem 1rem; background: #f9fafb; border-left: 4px solid #6366f1; border-radius: 8px; color: #1a1a1a; font-size: 0.9rem; line-height: 1.6;'>• {reason}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
    
    with comp_col_b:
        st.markdown(f"""
        <div style="padding: 2rem; background: #ffffff; border: 2px solid #e5e7eb; border-radius: 20px; margin-bottom: 1.5rem;">
            <h3 style="margin: 0 0 1.5rem 0; color: #1a1a1a; font-size: 1.5rem; font-weight: 700;">Contract B</h3>
            <div style="text-align: center; padding: 1.5rem; background: #f9fafb; border: 3px solid {score_color_b}; border-radius: 16px; margin-bottom: 1.5rem;">
                <div style="font-size: 0.85rem; color: #6b7280; margin-bottom: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Fairness Score</div>
                <div style="font-size: 3rem; font-weight: 800; color: {score_color_b};">{score_b}</div>
                <div style="font-size: 1rem; color: #6b7280; margin-top: 0.5rem; font-weight: 500;">out of 100</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Key fields
        fields_b = offer_b.get("fields", {}).get("core", {})
        st.markdown("<div style='color: #1a1a1a; font-weight: 700; font-size: 1.1rem; margin-bottom: 1rem;'>**Key Terms:**</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top: 0.75rem;'>", unsafe_allow_html=True)
        if fields_b.get("monthly_payment"):
            st.markdown(f"<div style='padding: 1rem; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; margin-bottom: 0.75rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'><strong style='color: #1a1a1a;'>Monthly Payment:</strong> <span style='color: #374151;'>{fields_b.get('monthly_payment')}</span></div>", unsafe_allow_html=True)
        if fields_b.get("apr"):
            st.markdown(f"<div style='padding: 1rem; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; margin-bottom: 0.75rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'><strong style='color: #1a1a1a;'>APR:</strong> <span style='color: #374151;'>{fields_b.get('apr')}</span></div>", unsafe_allow_html=True)
        if fields_b.get("term_months"):
            st.markdown(f"<div style='padding: 1rem; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; margin-bottom: 0.75rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'><strong style='color: #1a1a1a;'>Term:</strong> <span style='color: #374151;'>{fields_b.get('term_months')} months</span></div>", unsafe_allow_html=True)
        if fields_b.get("vehicle_price"):
            st.markdown(f"<div style='padding: 1rem; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; margin-bottom: 0.75rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'><strong style='color: #1a1a1a;'>Vehicle Price:</strong> <span style='color: #374151;'>{fields_b.get('vehicle_price')}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Score reasons
        reasons_b = offer_b.get("reasons", [])
        if reasons_b:
            with st.expander("📋 View Score Details"):
                st.markdown("<div style='display: flex; flex-direction: column; gap: 0.75rem; background: #ffffff; padding: 1rem; border-radius: 12px;'>", unsafe_allow_html=True)
                for reason in reasons_b[:5]:
                    st.markdown(f"<div style='padding: 0.875rem 1rem; background: #f9fafb; border-left: 4px solid #6366f1; border-radius: 8px; color: #1a1a1a; font-size: 0.9rem; line-height: 1.6;'>• {reason}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
    
    # Detailed comparison table
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**📊 Detailed Comparison:**", unsafe_allow_html=True)
    
    # Create comparison DataFrame
    comparison_data = []
    key_fields = ["monthly_payment", "apr", "term_months", "vehicle_price", "down_payment", "documentation_fee"]
    
    for field in key_fields:
        val_a = fields_a.get(field, "N/A")
        val_b = fields_b.get(field, "N/A")
        comparison_data.append({
            "Field": field.replace("_", " ").title(),
            "Contract A": val_a,
            "Contract B": val_b
        })
    
    if comparison_data:
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ================== FOOTER ==================
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown(f"""
<div class="footer">
    <p> Powered by <strong>Llama 3.1</strong> via Groq • FastAPI Backend: <code>{API_BASE_URL}</code></p>
    <p style="margin-top: 0.5rem; font-size: 0.85rem; opacity: 0.7;">Contract AI Analyzer v1.0 • Made with ❤️</p>
</div>
""", unsafe_allow_html=True)
