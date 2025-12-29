import streamlit as st
import pdfplumber
import tempfile
import os

from logic import (
    extract_fields,
    calculate_fairness_score,
    negotiation_advice,
    generate_summary,
    vin_lookup,
    get_recall_info_by_vin
)

from lease_chatbot import chatbot_response

st.set_page_config(page_title="Car Lease AI Assistant", layout="wide", page_icon="🚗")

# ---------- PDF TEXT EXTRACTION ----------
def extract_text_from_pdf(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        path = tmp.name

    text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"
    finally:
        os.remove(path)

    if not text.strip():
        raise ValueError("Scanned PDF detected. OCR not enabled.")
    return text

# ---------- HEADER ----------
st.markdown("<h1 style='text-align:center;'>🚗 Car Lease AI Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:gray;'>Upload • Analyze • Negotiate</p>", unsafe_allow_html=True)
st.divider()

# ---------- UPLOAD ----------
uploaded_pdf = st.file_uploader("📤 Upload Lease Contract (PDF)", type=["pdf"])

if not uploaded_pdf:
    st.info("Please upload a lease contract to begin.")
    st.stop()

try:
    text = extract_text_from_pdf(uploaded_pdf)
    st.success("PDF uploaded and processed successfully.")
except Exception as e:
    st.error(str(e))
    st.stop()

# ---------- ANALYSIS ----------
fields = extract_fields(text)
fairness_score, fairness_reasons = calculate_fairness_score(fields)
negotiation_tips = negotiation_advice(fields)
summary = generate_summary(fields, fairness_score, negotiation_tips)

vehicle = vin_lookup(fields["vin"]) if "vin" in fields else {}
recall = get_recall_info_by_vin(fields["vin"]) if "vin" in fields else {}

data = {
    "fields": fields,
    "fairness_score": fairness_score,
    "fairness_reasons": fairness_reasons,
    "negotiation_tips": negotiation_tips,
    "vehicle": vehicle,
    "recall": recall
}

# ---------- LAYOUT ----------
left, right = st.columns([2.2, 1])

with left:
    st.subheader("📄 Contract Summary")
    st.info(summary)

    st.subheader("💰 Key Details")
    c1, c2, c3 = st.columns(3)
    c1.metric("Monthly Payment", f"${fields.get('monthly_payment')}")
    c2.metric("APR", f"{fields.get('interest_rate')}%")
    c3.metric("Mileage / Year", fields.get("mileage_allowance"))

    st.subheader("📊 Fairness Score")
    st.progress(fairness_score / 100)
    for r in fairness_reasons:
        st.warning(r)

    st.subheader("🤝 Negotiation Tips")
    for tip in negotiation_tips:
        st.error(tip)

with right:
    st.subheader("🤖 Lease Chatbot")
    user_input = st.text_input("Ask a question")
    if user_input:
        st.success(chatbot_response(user_input, data))
