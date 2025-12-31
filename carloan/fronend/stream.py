import streamlit as st
import requests

ANALYZE_API = "http://127.0.0.1:8000/analyze"
CHAT_API = "http://127.0.0.1:8000/chat"

st.set_page_config(page_title="Car Lease AI", layout="wide")
st.title("🚗 Car Lease AI Assistant")

# -------------------- FILE UPLOAD --------------------
pdf = st.file_uploader("Upload Lease Contract", type="pdf")

analysis_result = None

if pdf:
    with st.spinner("Analyzing lease..."):
        response = requests.post(
            ANALYZE_API,
            files={"file": pdf.getvalue()}
        )

    if response.status_code != 200:
        st.error("Backend error occurred")
        st.code(response.text)
        st.stop()

    res = response.json()

    # 🔴 HANDLE BACKEND ERROR SAFELY
    if "error" in res:
        st.error("AI processing failed")
        st.code(res["error"])
        st.stop()

    analysis_result = res

    # -------------------- MAIN CONTENT --------------------
    st.subheader("📄 AI Summary")
    st.info(res.get("summary", "No summary generated"))

    st.subheader("🚗 VIN Verification")
    if res.get("vin_info", {}).get("valid"):
        st.success(res["vin_info"])
    else:
        st.warning("VIN not found or invalid")

    st.subheader("📊 Fairness Score")
    st.progress(res.get("fairness_score", 0) / 100)

    for r in res.get("fairness_reasons", []):
        st.warning(r)

    st.subheader("🤝 Negotiation Tips")
    for t in res.get("negotiation_tips", []):
        st.error(t)

# -------------------- SIDEBAR CHATBOT --------------------
st.sidebar.title("🤖 Lease Chatbot")

if analysis_result:
    user_question = st.sidebar.text_input(
        "Ask about this lease",
        placeholder="Is this a good deal?"
    )

    if user_question:
        # ✅ FIXED SPINNER (GLOBAL, NOT SIDEBAR)
        with st.spinner("Thinking..."):
            chat_response = requests.post(
                CHAT_API,
                json={
                    "question": user_question,
                    "data": analysis_result
                }
            )

        if chat_response.status_code == 200:
            st.sidebar.success(chat_response.json().get("answer"))
        else:
            st.sidebar.error("Chatbot error")

else:
    st.sidebar.info("Upload a lease PDF to enable chatbot.")
