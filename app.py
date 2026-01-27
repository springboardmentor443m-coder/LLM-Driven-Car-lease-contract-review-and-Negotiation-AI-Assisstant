import streamlit as st
import requests
import json

API_URL = "http://127.0.0.1:8000"

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="AI Lease Assistant",
    page_icon="🚗",
    layout="wide",
)

# -------------------------------------------------
# CSS
# -------------------------------------------------
st.markdown("""
<style>
html, body {
    font-family: 'Inter', sans-serif;
    background-color: #F7F9FC;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #0F172A;
    padding: 24px;
}
.stSidebar h1, .stSidebar h2, .stSidebar p {
    color: #E5E7EB;
}
.stSidebar img {
    margin-bottom: 20px;
}

/* NAV BUTTONS */
.stSidebar .stButton > button {
    width: 100%;
    text-align: left;
    background: transparent;
    color: #CBD5E1;
    padding: 12px 16px;
    border-radius: 14px;
    border: none;
    font-size: 16px;
    font-weight: 500;
    transition: all 0.25s ease;
}

.stSidebar .stButton > button:hover {
    background: rgba(37,99,235,0.18);
    color: #FFFFFF;
    transform: translateX(4px);
}

.nav-active button {
    background: linear-gradient(135deg,#2563EB,#1D4ED8) !important;
    color: white !important;
    font-weight: 600;
    box-shadow: 0 6px 18px rgba(37,99,235,0.45);
}

/* Hero */
.hero {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: linear-gradient(135deg,#2563EB,#1E3A8A);
    padding: 40px;
    border-radius: 20px;
    margin-bottom: 35px;
    color: white;
}
.hero img { width: 360px; }
.hero h1 { font-size: 44px; margin-bottom: 10px; }
.hero p { font-size: 18px; opacity: 0.9; }

/* Feature Cards */
.feature-card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    text-align: center;
}
.feature-card img { width: 80px; margin-bottom: 15px; }

/* Cards */
.card {
    background: white;
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 8px 20px rgba(15,23,42,0.08);
    margin-bottom: 24px;
}

/* Metrics */
.metric {
    background: linear-gradient(135deg,#2563EB,#1D4ED8);
    color: white;
    padding: 22px;
    border-radius: 14px;
    text-align: center;
    font-size: 18px;
    font-weight: 600;
}

/* Upload */
.upload-box {
    background-color: #F1F5F9;
    padding: 25px;
    border-radius: 14px;
    border: 2px dashed #CBD5E1;
}

/* Chat */
.chat-box {
    background-color: #F8FAFC;
    padding: 15px;
    border-radius: 14px;
    max-height: 420px;
    overflow-y: auto;
}
.user-msg {
    background: #DBEAFE;
    padding: 12px 16px;
    border-radius: 20px;
    margin: 6px 0;
}
.ai-msg {
    background: #EDE9FE;
    padding: 12px 16px;
    border-radius: 20px;
    margin: 6px 0;
}

/* Empty */
.empty {
    text-align: center;
    padding: 40px;
    opacity: 0.8;
}
.empty img { width: 220px; margin-bottom: 20px; }

footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/744/744465.png", width=70)
st.sidebar.title("AI Lease Assistant")
st.sidebar.caption("Contract Intelligence Platform")

if "page" not in st.session_state:
    st.session_state.page = "Contract Analysis"

def nav_button(label, icon):
    active = st.session_state.page == label
    container = st.sidebar.container()
    if active:
        container.markdown('<div class="nav-active">', unsafe_allow_html=True)
    if container.button(f"{icon}  {label}"):
        st.session_state.page = label
    if active:
        container.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("### Navigation")
nav_button("Contract Analysis", "📄")
nav_button("AI Chat", "🤖")
nav_button("Reports", "📊")
nav_button("About", "ℹ️")

st.sidebar.markdown("---")
st.sidebar.caption("🚗 AI Lease Assistant v1.0")

# -------------------------------------------------
# HERO
# -------------------------------------------------
st.markdown("""
<div class="hero">
    <div>
        <h1>AI Lease Contract Intelligence</h1>
        <p>Analyze lease contracts, detect risks, and negotiate smarter with AI.</p>
    </div>
    <img src="https://media.istockphoto.com/id/2149895112/vector/car-insurance-solid-icon-that-can-be-applied-anywhere-simple-pixel-perfect-and-modern-style.jpg?b=1&s=170x170&k=20&c=dxMTlbxHNy5W3HetT6LZv3IfrkESxJCMyCyaeYhIebM=">
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# FEATURES
# -------------------------------------------------
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="feature-card">
        <img src="https://cdn-icons-png.flaticon.com/512/942/942748.png">
        <h4>Contract Analysis</h4>
        <p>Extract lease terms and hidden clauses.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="feature-card">
        <img src="https://cdn-icons-png.flaticon.com/512/4712/4712100.png">
        <h4>Risk Detection</h4>
        <p>Identify financial and legal risks.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="feature-card">
        <img src="https://cdn-icons-png.flaticon.com/512/4712/4712035.png">
        <h4>AI Negotiation</h4>
        <p>Lower costs with smart AI advice.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------
# PAGES
# -------------------------------------------------
if st.session_state.page == "Contract Analysis":
    st.subheader("📂 Upload Lease Contract")
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("PDF or Image", type=["pdf","png","jpg","jpeg"])
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file and st.button("Analyze Contract"):
        with st.spinner("Analyzing..."):
            files = {"file": uploaded_file.getvalue()}
            res = requests.post(f"{API_URL}/analyze", files=files)
            if res.status_code == 200:
                data = res.json()
                sla = data.get("sla", {})
                risk = data.get("risk", {})

                m1, m2, m3 = st.columns(3)
                m1.markdown(f'<div class="metric">APR<br>{sla.get("APR","-")}</div>', unsafe_allow_html=True)
                m2.markdown(f'<div class="metric">Monthly<br>{sla.get("Monthly Payment","-")}</div>', unsafe_allow_html=True)
                m3.markdown(f'<div class="metric">Term<br>{sla.get("Lease Term","-")}</div>', unsafe_allow_html=True)

                c1, c2 = st.columns([2,1])
                with c1:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.subheader("Contract Terms")
                    st.json(sla)
                    st.markdown('</div>', unsafe_allow_html=True)

                with c2:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.subheader("Risk Assessment")
                    st.markdown(f"**Level:** {risk.get('level','Unknown')}")
                    st.write(risk.get("explanation",""))
                    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "AI Chat":
    st.subheader("🤖 Lease Negotiation Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if not st.session_state.chat_history:
        st.markdown("""
        <div class="empty">
            <img src="https://illustrations.popsy.co/gray/chatting.svg">
            <p>Ask about risks, penalties, or negotiation tips.</p>
        </div>
        """, unsafe_allow_html=True)

    q = st.text_input("Ask your question")
    if st.button("Send"):
        r = requests.post(f"{API_URL}/chat", json={"question": q})
        if r.status_code == 200:
            a = r.json().get("answer","")
            st.session_state.chat_history += [("You", q), ("AI", a)]

    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for s, m in st.session_state.chat_history:
        st.markdown(
            f'<div class="{"user-msg" if s=="You" else "ai-msg"}">{m}</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "Reports":
    st.markdown("""
    <div class="empty">
        <img src="https://illustrations.popsy.co/blue/data-analysis.svg">
        <h4>Reports Coming Soon</h4>
        <p>Analytics and comparisons will appear here.</p>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == "About":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("""
    **AI Lease Assistant** uses OCR and LLMs to analyze car lease contracts,
    detect risks, and provide negotiation guidance.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

st.caption("© 2026 AI Lease Intelligence Platform")
