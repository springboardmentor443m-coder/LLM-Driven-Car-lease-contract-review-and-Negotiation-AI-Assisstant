import streamlit as st
import requests

st.set_page_config(page_title="LeaseAI", layout="wide")

# ---------- LUXURY CSS STYLE ----------
st.markdown("""
<style>
body {
    background-color: #FAFAF7;
    font-family: 'Inter', sans-serif;
}
.section-card {
    background: white;
    padding: 26px;
    border: 1px solid #E5E1DD;
    border-radius: 10px;
    margin-bottom: 20px;
}
.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 10px;
}
.summary-header {
    font-size: 16px;
    margin-bottom: 20px;
    color: #444;
}
.label {
    font-weight: 600;
}
.tip-badge {
    background: #FFF7D6;
    padding: 10px 14px;
    border-radius: 6px;
    border: 1px solid #E9DCA8;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)


# ---------- SESSION ----------
if "analysis" not in st.session_state:
    st.session_state.analysis = None


# ---------- LANDING PAGE ----------
if st.session_state.analysis is None:

    st.markdown("""
    ### Lease Contract Intelligence  
    Upload your vehicle lease PDF and receive structured AI-powered analysis.
    """)

    file = st.file_uploader("Upload Lease PDF", type=["pdf"])

    if file:
        res = requests.post("http://127.0.0.1:8000/analyze", files={"file": file.getvalue()})
        st.session_state.analysis = res.json()
        st.rerun()

    st.stop()



analysis = st.session_state.analysis

tabs = st.tabs(["Summary", "Fairness Score", "Negotiation Tips", "VIN Info", "Chat"])


# ============= SUMMARY TAB =================
with tabs[0]:
    summary = analysis["summary"]

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Document Summary</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='summary-header'>{summary['contract_header']}</div>", unsafe_allow_html=True)

    # --- Terms ---
    st.markdown("<div class='label'>Key Terms:</div>", unsafe_allow_html=True)
    st.write("")
    st.markdown("<ul>", unsafe_allow_html=True)
    for k, v in summary["terms"].items():
        st.markdown(f"<li><b>{k}:</b> {v}</li>", unsafe_allow_html=True)
    st.markdown("</ul>", unsafe_allow_html=True)

    # --- Risks ---
    st.markdown("<div class='label'>Risks:</div>", unsafe_allow_html=True)
    st.markdown("<ul>", unsafe_allow_html=True)
    for r in summary["risks"]:
        st.markdown(f"<li>{r}</li>", unsafe_allow_html=True)
    st.markdown("</ul>", unsafe_allow_html=True)

    # --- Negotiation Advice ---
    st.markdown("<div class='label'>Negotiation Advice:</div>", unsafe_allow_html=True)
    st.markdown("<ul>", unsafe_allow_html=True)
    for n in summary["negotiation_advice"]:
        st.markdown(f"<li>{n}</li>", unsafe_allow_html=True)
    st.markdown("</ul>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)



# ============= FAIRNESS TAB =================
with tabs[1]:
    fairness = analysis["fairness"]
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Fairness Score</div>", unsafe_allow_html=True)

    st.write(f"Score: **{fairness['score']} / 100**")
    st.progress(fairness["score"] / 100)

    for r in fairness["reason"]:
        st.markdown(f"<div class='tip-badge'>{r}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)



# ============= NEGOTIATION TAB =================
with tabs[2]:
    tips = analysis["negotiation_tips"]
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Negotiation Tips</div>", unsafe_allow_html=True)

    for t in tips:
        st.markdown(f"<div class='tip-badge'>{t}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)



# ============= VIN INFO TAB =================
with tabs[3]:
    vin = analysis["vin"]
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>VIN Information</div>", unsafe_allow_html=True)

    if vin["valid"]:
        st.success(f"Valid VIN — {vin['vehicle']}")
    else:
        st.warning("VIN not valid")

    st.markdown("</div>", unsafe_allow_html=True)



# ============= CHAT TAB =================
with tabs[4]:
    q = st.text_input("Ask the AI about your lease:")
    if q:
        reply = requests.post("http://127.0.0.1:8000/chat", json={"question": q, "data": analysis}).json()
        st.success(reply["answer"])
