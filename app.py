import streamlit as st
import os
from pathlib import Path
from typing import Dict
import pandas as pd

from contract_extractor import (
    ocr_images_to_texts,
    extract_fields,
    add_negotiation_suggestions,
    generate_simple_explanation
)
from llm import call_groq
from assistant import build_prompt as chatbot_prompt_builder
from pdf2image import convert_from_path


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="LeaseIQ – Intelligent Contract Assistant",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "contracts" not in st.session_state:
    st.session_state.contracts: Dict[str, dict] = {}

if "summaries" not in st.session_state:
    st.session_state.summaries = {}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = True


# ---------------- STATS ----------------
contract_count = len(st.session_state.contracts)

field_count = sum(
    len(v.get("fields", {}))
    for v in st.session_state.contracts.values()
) if st.session_state.contracts else 0

risk_count = sum(
    len(v.get("negotiation_suggestions", []))
    for v in st.session_state.contracts.values()
) if st.session_state.contracts else 0


def overall_risk_level(count):
    if count == 0:
        return "LOW"
    elif count <= 5:
        return "MEDIUM"
    return "HIGH"


risk_level = overall_risk_level(risk_count)


# ---------------- GLOBAL STYLING ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #140a28, #2b1055);
}
.dashboard {
    background: rgba(60,30,120,0.95);
    border-radius: 18px;
    padding: 1.4rem;
    box-shadow: 0 20px 40px rgba(0,0,0,0.5);
}
.low {color:#2ecc71;}
.medium {color:#f1c40f;}
.high {color:#e74c3c;}
</style>
""", unsafe_allow_html=True)


# ---------------- HEADER ----------------
left, right = st.columns([8, 2])

with left:
    st.title("LeaseIQ – Intelligent Contract Assistant")
    st.caption(
        "AI-powered analysis of vehicle lease contracts to identify costs, risks, "
        "and negotiation opportunities."
    )

with right:
    if st.button("📊 Toggle Dashboard"):
        st.session_state.show_dashboard = not st.session_state.show_dashboard
        st.rerun()


# ---------------- MAIN LAYOUT ----------------
main_col, dash_col = st.columns([8, 3])


# ---------------- MAIN CONTENT ----------------
with main_col:
    st.subheader("📄 Upload Lease Documents")

    uploaded_files = st.file_uploader(
        "Upload one or more lease agreement PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("🚀 Analyze Contracts"):
            with st.spinner("Analyzing contracts..."):
                st.session_state.contracts.clear()
                st.session_state.summaries.clear()

                os.makedirs("uploaded_pdfs", exist_ok=True)
                os.makedirs("page_images", exist_ok=True)

                for pdf in uploaded_files:
                    pdf_path = f"uploaded_pdfs/{pdf.name}"

                    with open(pdf_path, "wb") as f:
                        f.write(pdf.getbuffer())

                    images = convert_from_path(pdf_path, dpi=300)
                    image_paths = []

                    for i, img in enumerate(images):
                        img_path = f"page_images/{pdf.name}_{i}.png"
                        img.save(img_path)
                        image_paths.append(Path(img_path))

                    texts = ocr_images_to_texts(image_paths)
                    result = extract_fields(texts)
                    add_negotiation_suggestions(result)
                    generate_simple_explanation(result)

                    st.session_state.contracts[pdf.name] = result
                    st.session_state.summaries[pdf.name] = call_groq(
                        f"Summarize this contract in 4–6 simple lines:\n{result}"
                    )

            st.success("✅ Contract analysis completed")

    # -------- CONTRACT SUMMARIES --------
    if st.session_state.summaries:
        st.subheader("📄 Contract Summaries")
        for name, summary in st.session_state.summaries.items():
            with st.expander(name):
                st.write(summary)

    # -------- RISK DETAILS (FIXED) --------
    if st.session_state.contracts:
        st.subheader("⚠️ Contract Risk Analysis")

        for contract_name, data in st.session_state.contracts.items():
            risks = data.get("negotiation_suggestions", [])

            if not risks:
                continue

            with st.expander(f"🔍 Risks in {contract_name}"):
                for i, risk in enumerate(risks, start=1):

                    # Case 1: structured risk (dict)
                    if isinstance(risk, dict):
                        clause = risk.get("clause", "Unspecified Clause")
                        issue = risk.get("issue", "Potential contractual risk")
                        severity = risk.get("severity", "Medium").upper()
                        suggestion = risk.get(
                            "suggestion",
                            "Consider negotiating this clause"
                        )

                    # Case 2: unstructured risk (string)
                    else:
                        clause = "Risky Clause Detected"
                        issue = risk
                        severity = "MEDIUM"
                        suggestion = "Review and negotiate this clause"

                    badge = {
                        "LOW": "🟢",
                        "MEDIUM": "🟡",
                        "HIGH": "🔴"
                    }.get(severity, "🟡")

                    st.markdown(
                        f"""
**{badge} Risk {i}: {clause}**

- **Issue:** {issue}
- **Severity:** {severity}
- **Why this matters:** This clause may increase financial or legal exposure.
- **Suggested action:** {suggestion}
"""
                    )


# ---------------- DASHBOARD ----------------
if st.session_state.show_dashboard:
    with dash_col:
        with st.container():
            st.markdown('<div class="dashboard">', unsafe_allow_html=True)

            st.subheader("📊 Contract Overview")
            st.metric("Contracts Uploaded", contract_count)
            st.metric("Fields Extracted", field_count)
            st.metric("Risk Points", risk_count)

            st.markdown(
                f"⚠️ **Overall Risk Level:** "
                f"<span class='{risk_level.lower()}'>{risk_level}</span>",
                unsafe_allow_html=True
            )

            if st.session_state.contracts:
                rows = []
                for name, data in st.session_state.contracts.items():
                    row = {"Contract": name}
                    row.update(data.get("fields", {}))
                    rows.append(row)

                df = pd.DataFrame(rows)
                st.download_button(
                    "📤 Export Report (CSV)",
                    data=df.to_csv(index=False),
                    file_name="leaseiq_report.csv",
                    mime="text/csv"
                )

            st.markdown('</div>', unsafe_allow_html=True)


# ---------------- CHATBOT ----------------
if st.session_state.contracts:
    st.subheader("💬 Ask the Contract Expert")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Ask about clauses, risks, or contract differences...")

    if question:
        st.session_state.chat_history.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("assistant"):
            answer = call_groq(
                chatbot_prompt_builder(
                    st.session_state.contracts,
                    st.session_state.summaries,
                    question
                )
            )
            st.markdown(answer)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": answer}
        )
