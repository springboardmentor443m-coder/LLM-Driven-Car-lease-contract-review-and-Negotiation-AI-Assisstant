import streamlit as st
import sys
import os

# FIX BACKEND IMPORT PATH

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from backend.ocr_extractor import extract_text, extract_vin
from backend.vin_decoder import decode_vin
from backend.llm_analyzer import analyze_contract, analyze_with_llm
from backend.price_estimator import estimate_price
from backend.chatbot import chatbot_response

# PAGE CONFIG

st.set_page_config(
    page_title="Car Lease AI Assistant",
    page_icon="🚗",
    layout="wide"
)

# GLOBAL GLASSMORPHISM + CAR THEME

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }

    section[data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.55);
        backdrop-filter: blur(14px);
        border-right: 1px solid rgba(255,255,255,0.1);
    }

    .glass {
        background: rgba(255, 255, 255, 0.12);
        border-radius: 18px;
        padding: 22px;
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.4);
        margin-bottom: 22px;
    }

    .hero {
        padding: 40px;
        text-align: center;
    }

    .hero h1 {
        font-size: 42px;
        font-weight: 700;
    }

    .hero p {
        color: #d0d0d0;
        font-size: 18px;
    }

    .stButton > button {
        background: linear-gradient(135deg, #ff512f, #dd2476);
        color: white;
        border-radius: 30px;
        padding: 10px 28px;
        font-size: 16px;
        border: none;
        transition: 0.3s ease;
    }

    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(255, 81, 47, 0.8);
    }

    textarea {
        background: rgba(0,0,0,0.45) !important;
        color: white !important;
        border-radius: 12px !important;
    }

    div[data-testid="metric-container"] {
        background: rgba(255,255,255,0.15);
        border-radius: 14px;
        padding: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# SESSION STATE

if "ai_result" not in st.session_state:
    st.session_state.ai_result = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

extracted_text = ""
vehicle_data = None

# SIDEBAR NAVIGATION (STANDARD PRODUCT STYLE)
with st.sidebar:
    st.title("🚗 Car Lease AI")
    st.caption("Smart Contract Assistant")

    page = st.radio(
        "Navigate",
        ["🏠 Dashboard", "📄 Contract Review", "💬 AI Assistant", "🚘 VIN Decoder"]
    )

    st.markdown("---")
    st.markdown(
        """
        ✔ OCR Contract Reading  
        ✔ Risk Detection  
        ✔ AI Review  
        ✔ Price Estimation  
        ✔ Chatbot Support  
        """
    )

#  DASHBOARD (HOME PAGE)

if page == "🏠 Dashboard":

    st.markdown(
        """
        <div class="glass hero">
            <h1>🚗 Car Lease AI Assistant</h1>
            <p>
            Upload contracts • Detect risks • Estimate true cost • Negotiate smarter
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="glass">
                <h3>📄 Contract Analysis</h3>
                <p>OCR-based extraction and risk detection from lease agreements.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="glass">
                <h3>🧠 AI Review</h3>
                <p>LLM-powered legal insights and negotiation suggestions.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="glass">
                <h3>💰 Cost Estimation</h3>
                <p>Understand real cost per mile and long-term lease impact.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

#  CONTRACT REVIEW PAGE

elif page == "📄 Contract Review":

    st.markdown('<div class="glass">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "📄 Upload Car Lease Agreement",
        type=["pdf", "png", "jpg", "jpeg"]
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file:
        os.makedirs("data", exist_ok=True)
        file_path = os.path.join("data", uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        extracted_text = extract_text(file_path)

        if extracted_text.strip():

            tab1, tab2, tab3 = st.tabs(
                ["📄 Contract Text", "⚠ Risk Analysis", "🤖 AI Review"]
            )

            # TAB 1
            with tab1:
                st.markdown('<div class="glass">', unsafe_allow_html=True)
                st.text_area("Extracted Text", extracted_text, height=400)
                st.markdown('</div>', unsafe_allow_html=True)

            # TAB 2
            with tab2:
                st.markdown('<div class="glass">', unsafe_allow_html=True)

                vin = extract_vin(extracted_text)
                if vin:
                    vehicle_data = decode_vin(vin)
                    st.success(f"VIN Detected: {vin}")
                    st.write(vehicle_data)

                risks = analyze_contract(extracted_text)
                for r in risks:
                    st.error(r["risk"])
                    st.info(r["negotiation_tip"])

                st.markdown('</div>', unsafe_allow_html=True)

            # TAB 3
            with tab3:
                st.markdown('<div class="glass">', unsafe_allow_html=True)

                if st.button("Run AI Contract Analysis"):
                    with st.spinner("Analyzing..."):
                        st.session_state.ai_result = analyze_with_llm(extracted_text)

                if st.session_state.ai_result:
                    st.markdown(st.session_state.ai_result)

                st.markdown('</div>', unsafe_allow_html=True)

# AI CHATBOT

elif page == "💬 AI Assistant":

    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("💬 Lease Assistant")

    question = st.text_input("Ask anything about lease, EMI, risks, negotiation")

    if st.button("Ask AI"):
        reply = chatbot_response(question, extracted_text, vehicle_data)
        st.session_state.chat_history.append(("You", question))
        st.session_state.chat_history.append(("AI", reply))

    for sender, msg in st.session_state.chat_history:
        st.markdown(f"**{sender}:** {msg}")

    st.markdown('</div>', unsafe_allow_html=True)

#  VIN DECODER

else:

    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("🔍 VIN Decoder")

    vin_input = st.text_input("Enter VIN")

    if st.button("Decode"):
        vehicle_data = decode_vin(vin_input)
        if vehicle_data:
            st.success("Decoded Successfully")
            st.write(vehicle_data)
        else:
            st.error("Invalid VIN")

    st.markdown('</div>', unsafe_allow_html=True)
