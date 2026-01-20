import streamlit as st
import sys
import os
import plotly.graph_objects as go

# --------------------------------------------------
# PATH FIX
# --------------------------------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from backend.ocr_extractor import extract_text, extract_vin
from backend.vin_decoder import decode_vin
from backend.llm_analyzer import analyze_contract, analyze_with_llm
from backend.chatbot import chatbot_response

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Car Lease AI Assistant",
    page_icon="🚘",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS FUNCTION
# --------------------------------------------------
def load_luxury_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #0E1117;
        color: #C0C0C0;
    }

    section[data-testid="stSidebar"] {
        background-color: #11151C;
        border-right: 1px solid #1f2937;
    }

    h1, h2, h3 {
        color: #ffffff;
    }

    .hero {
        text-align: center;
        padding: 50px 20px;
    }

    .hero h1 {
        font-size: 46px;
        font-weight: 700;
    }

    .hero p {
        font-size: 18px;
        color: #9ca3af;
    }

    .metric-card {
        background: linear-gradient(145deg, #141824, #0b0f17);
        border-radius: 14px;
        padding: 22px;
        text-align: center;
        border: 1px solid #1f2937;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }

    .metric-card h2 {
        color: #007BFF;
        font-size: 32px;
        margin-bottom: 6px;
    }

    .metric-card span {
        color: #9ca3af;
        font-size: 14px;
    }

    button, input, textarea {
        border-radius: 10px !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #007BFF, #0056b3);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 22px;
        font-weight: 600;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #0056b3, #003f88);
    }

    </style>
    """, unsafe_allow_html=True)


load_luxury_css()

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
st.session_state.setdefault("chat_history", [])
st.session_state.setdefault("contract_text", "")
st.session_state.setdefault("vehicle_data", None)
st.session_state.setdefault("ai_result", None)

# --------------------------------------------------
# SIDEBAR – VEHICLE FILTERS
# --------------------------------------------------
with st.sidebar:
    st.title("🚘 Vehicle Filters")

    st.selectbox("Brand", ["All", "BMW", "Audi", "Mercedes", "Porsche"])
    st.slider("Model Year", 2015, 2025, (2019, 2024))
    st.slider("Price Range ($)", 20000, 200000, (40000, 120000))

    st.divider()

    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "📄 Contract Review", "💬 AI Assistant", "🚘 VIN Decoder"]
    )

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------
if page == "🏠 Dashboard":

    st.markdown("""
    <div class="hero">
        <h1>Luxury Car Lease Intelligence</h1>
        <p>AI-powered insights for premium automotive contracts</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # METRIC CARDS
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="metric-card">
            <h2>250 km/h</h2>
            <span>Top Speed</span>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="metric-card">
            <h2>450 HP</h2>
            <span>Horsepower</span>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="metric-card">
            <h2>14 km/l</h2>
            <span>Efficiency</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # FEATURE GALLERY
    with st.expander("🚗 Feature Gallery"):
        st.image(
            "https://via.placeholder.com/1200x400?text=Luxury+Car+Showcase",
            use_container_width=True
        )
        st.write("Premium interiors • Advanced safety • AI-driven performance")

    st.divider()

    # PERFORMANCE CHART
    st.subheader("📈 Performance Curve")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[0, 20, 40, 60, 80, 100],
        y=[0, 60, 120, 170, 210, 250],
        mode="lines+markers",
        line=dict(color="#007BFF", width=4)
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        xaxis_title="Time (s)",
        yaxis_title="Speed (km/h)"
    )

    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# CONTRACT REVIEW (FEATURE UNCHANGED)
# --------------------------------------------------
elif page == "📄 Contract Review":

    uploaded_file = st.file_uploader(
        "Upload Lease Contract",
        type=["pdf", "png", "jpg", "jpeg"]
    )

    if uploaded_file:
        os.makedirs("data", exist_ok=True)
        path = os.path.join("data", uploaded_file.name)

        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        text = extract_text(path)
        st.session_state.contract_text = text

        tabs = st.tabs(["📄 Text", "⚠ Risks", "🤖 AI Review"])

        with tabs[0]:
            st.text_area("Extracted Contract", text, height=400)

        with tabs[1]:
            vin = extract_vin(text)
            if vin:
                data = decode_vin(vin)
                st.session_state.vehicle_data = data
                st.success(f"VIN Detected: {vin}")
                st.write(data)

            for r in analyze_contract(text):
                st.error(r["risk"])
                st.info(r["negotiation_tip"])

        with tabs[2]:
            if st.button("Run AI Analysis"):
                st.session_state.ai_result = analyze_with_llm(text)
            if st.session_state.ai_result:
                st.markdown(st.session_state.ai_result)

# --------------------------------------------------
# AI ASSISTANT
# --------------------------------------------------
elif page == "💬 AI Assistant":

    st.subheader("💬 Gemini Lease Assistant")

    q = st.text_input("Ask anything about your lease")

    if st.button("Ask AI"):
        reply = chatbot_response(
            q,
            st.session_state.contract_text,
            st.session_state.vehicle_data
        )
        st.session_state.chat_history.append(("You", q))
        st.session_state.chat_history.append(("AI", reply))

    for sender, msg in st.session_state.chat_history:
        st.markdown(f"**{sender}:** {msg}")

# --------------------------------------------------
# VIN DECODER
# --------------------------------------------------
else:

    vin_input = st.text_input("Enter VIN")
    if st.button("Decode VIN"):
        data = decode_vin(vin_input)
        if data:
            st.success("Vehicle Decoded")
            st.write(data)
        else:
            st.error("Invalid VIN")
