import streamlit as st
import os
from pathlib import Path
from typing import Dict

from contract_extractor import (
    ocr_images_to_texts,
    extract_fields,
    add_negotiation_suggestions,
    generate_simple_explanation
)
from llm_groq import call_groq
from chatbot import build_prompt as chatbot_prompt_builder
from pdf2image import convert_from_path
import pandas as pd


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Car Lease AI Assistant",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ---------------- GLOBAL STYLES (ONLY STYLING ADDED) ----------------
st.markdown(
    """
    <style>

    /* Background */
    .stApp {
        background-image: url("https://images.hdqwalls.com/download/dark-dodge-challenger-pm-3840x2160.jpg");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        background-color: #000;
    }

    .main {
        background: rgba(0,0,0,0.85);
        padding: 2.8rem;
        border-radius: 22px;
        box-shadow: 0 0 30px rgba(0,229,255,0.12);
    }

    h1 {
        text-align: center;
        font-size: 3.2rem;
        font-weight: 900;
        color: #00e5ff;
        text-shadow: 0 0 14px rgba(0,229,255,0.9);
        margin-bottom: 0.5rem;
    }

    /* -------- Animated Intro Text -------- */
    @keyframes slideInLeft {
        0% {
            transform: translateX(-80px);
            opacity: 0;
        }
        100% {
            transform: translateX(0);
            opacity: 1;
        }
    }

    .intro-text {
        animation: slideInLeft 1.3s ease-out;
        color: #e0f7fa;
        font-size: 1.15rem;
        font-weight: 600;
        line-height: 1.7;
        max-width: 900px;
        margin: 1.6rem auto 2.2rem auto;
        text-align: center;
        text-shadow: 0 0 6px rgba(0,229,255,0.3);
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #ff1744, #ff5252);
        color: white;
        border-radius: 14px;
        border: none;
        padding: 0.75rem 1.7rem;
        font-weight: 800;
        transition: all 0.25s ease;
        box-shadow: 0 0 14px rgba(255,23,68,0.6);
    }

    .stButton>button:hover {
        transform: translateY(-2px) scale(1.06);
        box-shadow: 0 0 26px rgba(255,23,68,0.95);
    }

    .stExpander {
        background-color: rgba(18,18,18,0.92);
        border-radius: 16px;
        border: 1px solid rgba(0,229,255,0.35);
    }

    .stChatMessage {
        background-color: rgba(22,22,22,0.96);
        border-radius: 18px;
        padding: 1rem;
    }

    section[data-testid="stSidebar"] {
        background: rgba(0,0,0,0.95);
        border-right: 1px solid rgba(0,229,255,0.35);
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- TITLE ----------------
st.title("Car Lease Contract AI Assistant")
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("* Smart contract understanding")
with col2:
    st.caption("* Expert negotiation insights")
with col3:
    st.caption("* Multi-contract comparison")

# ---------------- INTRO TEXT (NEW SECTION) ----------------
st.markdown(
    """
    <div class="intro-text">
        This intelligent assistant helps you understand car lease contracts without legal confusion.<br>
        Upload one or more lease documents to uncover hidden costs, financial risks, and expert negotiation insights —
        all powered by AI in seconds.
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- DIRECTORIES ----------------
UPLOAD_DIR = "uploaded_pdfs"
IMAGE_DIR = "page_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

# ---------------- SESSION STATE ----------------
if "contracts" not in st.session_state:
    st.session_state.contracts: Dict[str, dict] = {}

if "summaries" not in st.session_state:
    st.session_state.summaries: Dict[str, str] = {}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- SIDEBAR DASHBOARD ----------------
with st.sidebar:
    st.markdown("## 📊 Dashboard")
    st.markdown("### Uploaded Contracts")

    if st.session_state.contracts:
        for name in st.session_state.contracts.keys():
            st.markdown(f"- 📄 **{name}**")
    else:
        st.markdown("_No contracts uploaded yet_")

    # -------- Comparison Button (ONLY if multiple docs) --------
    if len(st.session_state.contracts) > 1:
        st.markdown("---")
        if st.button("📊 Compare Contracts"):
            rows = []
            for name, data in st.session_state.contracts.items():
                row = {"Contract": name}
                row.update(data.get("fields", {}))
                rows.append(row)

            df = pd.DataFrame(rows)
            st.session_state["comparison_df"] = df

# ---------------- FILE UPLOAD ----------------
uploaded_files = st.file_uploader(
    "📤 Upload one or more lease PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

# ---------------- ANALYZE ----------------
if uploaded_files:
    if st.button("⚡ Analyze Contracts", use_container_width=True):
        with st.spinner("Analyzing contracts..."):

            st.session_state.contracts.clear()
            st.session_state.summaries.clear()

            for pdf in uploaded_files:
                contract_id = pdf.name
                pdf_path = os.path.join(UPLOAD_DIR, pdf.name)

                with open(pdf_path, "wb") as f:
                    f.write(pdf.getbuffer())

                images = convert_from_path(pdf_path, dpi=300)
                image_paths = []

                for i, img in enumerate(images):
                    img_path = os.path.join(IMAGE_DIR, f"{contract_id}_{i}.png")
                    img.save(img_path)
                    image_paths.append(Path(img_path))

                texts = ocr_images_to_texts(image_paths)
                result = extract_fields(texts)
                add_negotiation_suggestions(result)
                generate_simple_explanation(result)

                st.session_state.contracts[contract_id] = result

                summary_prompt = f"""
Write a SHORT, clear human-friendly summary (4–6 lines).
No numbering. No task labels.

Contract Data:
{result}

Summary:
"""
                st.session_state.summaries[contract_id] = call_groq(summary_prompt).strip()

        st.success("✅ All contracts analyzed successfully")

# ---------------- COMPARISON TABLE ----------------
if "comparison_df" in st.session_state:
    st.subheader("📊 Contract Comparison")
    st.dataframe(st.session_state["comparison_df"], use_container_width=True)

# ---------------- DISPLAY SUMMARIES ----------------
if st.session_state.summaries:
    st.subheader("📄 Contract Summaries")
    for cid, summary in st.session_state.summaries.items():
        with st.expander(cid):
            st.write(summary)

# ---------------- CHATBOT ----------------
if st.session_state.contracts:
    st.subheader("💬 Ask the Contract Expert")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_question = st.chat_input("Ask about risks, costs, or compare contracts...")

    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})

        with st.chat_message("assistant"):
            with st.spinner("Thinking like an expert..."):
                prompt = chatbot_prompt_builder(
                    st.session_state.contracts,
                    st.session_state.summaries,
                    user_question
                )
                answer = call_groq(prompt)
                st.markdown(answer)

        st.session_state.chat_history.append({"role": "assistant", "content": answer})
