import streamlit as st
import requests
import json
import pandas as pd

# ---------- CONFIG ----------
BACKEND = "http://127.0.0.1:8000"
st.set_page_config(page_title="Loan/Lease Contract AI", layout="wide")

# ---------- STYLES ----------
st.markdown(
    """
    <style>
    .big-title { font-size:34px; font-weight:700; }
    .muted { color: #b6b6b6; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- UTILITIES ----------
def api_post_json(path: str, json_body: dict, timeout=90):
    try:
        resp = requests.post(f"{BACKEND}{path}", json=json_body, timeout=timeout)
        resp.raise_for_status()
        return resp
    except Exception as e:
        try:
            return {"error": f"{str(e)} | details: {e.response.text}"}
        except:
            return {"error": str(e)}

def api_post_file(path: str, uploaded_file, timeout=120):
    try:
        filename = getattr(uploaded_file, "name", "file.pdf")
        file_bytes = uploaded_file.getvalue()
        content_type = getattr(uploaded_file, "type", "application/pdf") or "application/pdf"
        files = {"file": (filename, file_bytes, content_type)}
        resp = requests.post(f"{BACKEND}{path}", files=files, timeout=timeout)
        resp.raise_for_status()
        return resp
    except Exception as e:
        try:
            return {"error": f"{str(e)} | details: {e.response.text}"}
        except:
            return {"error": str(e)}

def api_get(path: str, timeout=20):
    try:
        resp = requests.get(f"{BACKEND}{path}", timeout=timeout)
        resp.raise_for_status()
        return resp
    except Exception as e:
        try:
            return {"error": f"{str(e)} | details: {e.response.text}"}
        except:
            return {"error": str(e)}

# ---------- SESSION STATE ----------
if "extracted" not in st.session_state:
    st.session_state.extracted = None
if "summary_response" not in st.session_state:
    st.session_state.summary_response = None
if "compare_response" not in st.session_state:
    st.session_state.compare_response = None
if "neg_polite" not in st.session_state:
    st.session_state.neg_polite = ""
if "neg_firm" not in st.session_state:
    st.session_state.neg_firm = ""
if "neg_legal" not in st.session_state:
    st.session_state.neg_legal = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- HEADER ----------
c1, c2 = st.columns([0.75, 0.25])
with c1:
    st.markdown('<div class="big-title"> Loan/Lease Contract AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Upload contracts, check VINs, compare offers and generate negotiation assets.</div>', unsafe_allow_html=True)

with c2:
    if st.button("🔄 Reset App"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.markdown("---")



# ===================================================================
# LEFT SIDE — UPLOAD CONTRACT
# ===================================================================
left, right = st.columns([0.65, 0.35])

with left:
    st.header("📄 Upload Contract PDF")
    uploaded = st.file_uploader("Select contract (PDF)", type=["pdf"], key="main_contract")

    if uploaded:
        st.info("📤 Uploading & Extracting…")
        with st.spinner("Running OCR + Extraction…"):
            resp = api_post_file("/extract", uploaded)

        if isinstance(resp, dict) and resp.get("error"):
            st.error("Extraction error: " + resp["error"])
        else:
            try:
                st.session_state.extracted = resp.json()
                st.success("✅ Extraction completed")
                
                raw_text = st.session_state.extracted.get("raw_text", "")
                if raw_text:
                    st.code(raw_text[:700] + "..." if len(raw_text) > 700 else raw_text)
                else:
                    st.warning("No text extracted from PDF")
                    
            except Exception as e:
                st.error(f"Failed to parse response: {e}")
                st.session_state.extracted = None

    if st.session_state.extracted:
        extracted_data = (
            st.session_state.extracted.get("llm_structured_data_full") or 
            st.session_state.extracted.get("llm_structured_data_important") or 
            st.session_state.extracted.get("llm_structured_data") or 
            {}
        )
        
        st.subheader("🧠 Extracted Fields")
        
        if extracted_data:
            if "core" in extracted_data:
                st.json(extracted_data["core"])
            else:
                st.json(extracted_data)
            
            def count_fields(obj):
                if isinstance(obj, dict):
                    return sum(1 for v in obj.values() if v not in ("", None, [], {}))
                return 0
            
            field_count = count_fields(extracted_data.get("core", extracted_data))
            st.success(f"✅ Extracted {field_count} fields")
        else:
            st.warning("⚠️ No fields extracted")

        with st.expander("Show full OCR text"):
            st.text_area("Raw OCR", st.session_state.extracted.get("raw_text", ""), height=300, key="raw_ocr_view")

# ===================================================================
# RIGHT SIDE — VIN LOOKUP (ENHANCED VERSION)
# ===================================================================
with right:
    st.header("🔍 VIN Lookup")
    vin_input = st.text_input("Enter VIN (17 chars)", key="vin_field")

    if st.button("🔎 Search VIN", key="btn_vin"):
        if len(vin_input.strip()) != 17:
            st.error("❌ VIN must be 17 characters")
        else:
            with st.spinner("Searching database..."):
                vin_resp = api_get(f"/vin/{vin_input.strip()}")

            if isinstance(vin_resp, dict) and vin_resp.get("error"):
                st.error(vin_resp["error"])
            else:
                try:
                    data = vin_resp.json()
                except:
                    st.error("Invalid response")
                    st.stop()

                status = data.get("status")
                
                if status == "invalid":
                    st.error("❌ Invalid VIN format")
                    
                elif status == "error":
                    st.warning(f"⚠️ {data.get('message', 'Lookup failed')}")
                    
                elif status == "found":
                    summary = data.get("summary", {})
                    
                    st.success("✅ VIN Found!")
                    st.markdown("---")
                    
                    # TITLE
                    year = summary.get("year", "?")
                    make = summary.get("make", "?")
                    model = summary.get("model", "?")
                    trim = summary.get("trim", "")
                    
                    st.markdown(f"##  {year} {make} {model}")
                    if trim and trim not in ("N/A", "", None):
                        st.markdown(f"**Trim:** {trim}")
                    
                    st.markdown("---")
                    
                    # 3 COLUMNS
                    c1, c2, c3 = st.columns(3)
                    
                    with c1:
                        st.markdown("**🔧 Engine**")
                        st.write(f"Type: {summary.get('engine', 'N/A')}")
                        st.write(f"Fuel: {summary.get('fuel', 'N/A')}")
                        st.write(f"Drive: {summary.get('drive_type', 'N/A')}")
                        
                    with c2:
                        st.markdown("**⚙️ Details**")
                        st.write(f"Trans: {summary.get('transmission', 'N/A')}")
                        st.write(f"Body: {summary.get('body_class', 'N/A')}")
                        st.write(f"Doors: {summary.get('doors', 'N/A')}")
                        
                    with c3:
                        st.markdown("**🏭 Origin**")
                        st.write(f"Made: {summary.get('manufactured_in', 'N/A')}")
                        st.write(f"Maker: {summary.get('manufacturer', 'N/A')}")
                        st.write(f"Type: {summary.get('vehicle_type', 'N/A')}")
                    
                    st.markdown("---")
                    st.info(f"**VIN:** `{summary.get('vin', vin_input)}`")

                    # FULL RAW DATA
                    with st.expander("🔎 Full NHTSA Database"):
                        raw = summary.get("raw", [])
                        
                        if raw and isinstance(raw, list):
                            st.write(f"**Total fields:** {len(raw)}")
                            
                            rows = []
                            for item in raw:
                                if isinstance(item, dict):
                                    val = item.get("Value", "")
                                    if val and val not in ("", "Not Applicable", "N/A", "0"):
                                        rows.append({
                                            "ID": item.get("VariableId", ""),
                                            "Field": item.get("Variable", ""),
                                            "Value": val
                                        })
                            
                            if rows:
                                df = pd.DataFrame(rows)
                                st.dataframe(df, use_container_width=True, height=400)
                                
                                csv = df.to_csv(index=False)
                                st.download_button("📥 Download CSV", csv, f"vin_{vin_input}.csv", "text/csv")
                            else:
                                st.info("No additional data")
                        else:
                            st.warning("No raw data returned")
                            
                else:
                    st.warning("❌ VIN not found")

# ===================================================================
# SUMMARY + FAIRNESS + NEGOTIATION
# ===================================================================
st.markdown("---")
st.header("📊 Summary & Fairness")

if st.session_state.extracted:
    if st.button("Generate Summary, Score & Negotiation"):
        extracted_data = (
            st.session_state.extracted.get("llm_structured_data_full") or 
            st.session_state.extracted.get("llm_structured_data") or 
            {}
        )
        
        payload = {
            "raw_text": st.session_state.extracted.get("raw_text", ""),
            "llm_structured_data_full": extracted_data
        }

        with st.spinner("Processing..."):
            resp = api_post_json("/summarize", payload)

        if isinstance(resp, dict) and resp.get("error"):
            st.error(resp["error"])
        else:
            st.session_state.summary_response = resp.json()
            st.success("✅ Summary generated!")

    if st.session_state.summary_response:
        s = st.session_state.summary_response
        summary = s.get("summary", {})
        fairness = s.get("fairness_score", 0)
        reasons = s.get("score_reasons", [])
        negotiation = s.get("negotiation_tips", {})

        if not st.session_state.neg_polite:
            st.session_state.neg_polite = negotiation.get("polite", "")
        if not st.session_state.neg_firm:
            st.session_state.neg_firm = negotiation.get("firm", "")
        if not st.session_state.neg_legal:
            st.session_state.neg_legal = negotiation.get("legal_based", "")

        c1, c2, c3 = st.columns([2, 1, 1])

        with c1:
            st.subheader("Plain Summary")
            st.write(summary.get("plain_summary", "No summary"))
            st.caption(f"Confidence: {summary.get('confidence', 'unknown')}")

        with c2:
            st.subheader("Red Flags")
            flags = summary.get("red_flags", [])
            if flags:
                for f in flags:
                    st.error(f)
            else:
                st.success("✅ None")

        with c3:
            st.subheader("Fairness Score")
            
            if fairness >= 80:
                st.metric("Score", f"{fairness}/100", delta="Good", delta_color="normal")
            elif fairness >= 60:
                st.metric("Score", f"{fairness}/100", delta="Average", delta_color="off")
            else:
                st.metric("Score", f"{fairness}/100", delta="Bad", delta_color="inverse")
            
            st.write("### Deductions:")
            for r in reasons:
                st.write("•", r)

        st.markdown("### ✏️ Negotiation Messages")
        st.session_state.neg_polite = st.text_area("Polite", st.session_state.neg_polite, height=150, key="p")
        st.session_state.neg_firm = st.text_area("Firm", st.session_state.neg_firm, height=150, key="f")
        st.session_state.neg_legal = st.text_area("Legal", st.session_state.neg_legal, height=150, key="l")

        if st.button("📥 Download PDF"):
            pdf_payload = {
                "summary": summary,
                "fairness_score": fairness,
                "score_reasons": reasons,
                "negotiation_tips": {
                    "polite": st.session_state.neg_polite,
                    "firm": st.session_state.neg_firm,
                    "legal_based": st.session_state.neg_legal
                },
                "structured_data": st.session_state.extracted.get("llm_structured_data_full", {})
            }

            with st.spinner("Generating PDF…"):
                pdf_resp = api_post_json("/negotiation_pdf", pdf_payload)

            if isinstance(pdf_resp, dict) and pdf_resp.get("error"):
                st.error("PDF Error: " + pdf_resp["error"])
            else:
                st.download_button("📄 Download", pdf_resp.content, "negotiation_report.pdf", "application/pdf")
else:
    st.info("👆 Upload a contract PDF first")

# ===================================================================
# OFFER COMPARISON
# ===================================================================
st.markdown("---")
st.header("📑 Compare Two Offers")

c1, c2 = st.columns(2)
with c1:
    offerA = st.file_uploader("Offer A", type=["pdf"], key="offerA")
with c2:
    offerB = st.file_uploader("Offer B", type=["pdf"], key="offerB")

if st.button("Compare"):
    if not offerA or not offerB:
        st.error("Upload both offers")
    else:
        with st.spinner("Extracting..."):
            A = api_post_file("/extract", offerA)
            B = api_post_file("/extract", offerB)

        if isinstance(A, dict) and A.get("error"):
            st.error(f"A Error: {A['error']}")
        elif isinstance(B, dict) and B.get("error"):
            st.error(f"B Error: {B['error']}")
        else:
            structA = A.json().get("llm_structured_data_full") or A.json().get("llm_structured_data", {})
            structB = B.json().get("llm_structured_data_full") or B.json().get("llm_structured_data", {})
            
            cmp_resp = api_post_json("/compare_offers", {"offer_a": structA, "offer_b": structB})

            if isinstance(cmp_resp, dict) and cmp_resp.get("error"):
                st.error(cmp_resp["error"])
            else:
                st.session_state.compare_response = cmp_resp.json()

if st.session_state.compare_response:
    cmp = st.session_state.compare_response
    st.write("### 📊 Results")

    def get_core(offer):
        return offer["core"] if "core" in offer else offer
    
    A_core = get_core(cmp["offer_a"]["fields"])
    B_core = get_core(cmp["offer_b"]["fields"])
    
    fields = [
        ("Buyer", "buyer_name"), ("Seller", "seller_name"), ("VIN", "vin"),
        ("Year", "year"), ("Make", "make"), ("Model", "model"),
        ("Monthly Payment", "monthly_payment"), ("APR", "apr"),
        ("Term", "term_months"), ("Price", "vehicle_price"),
    ]
    
    df_data = []
    for label, key in fields:
        val_a = A_core.get(key, "—")
        val_b = B_core.get(key, "—")
        if val_a in ("", "—", None) and val_b in ("", "—", None):
            continue
        df_data.append({"Field": label, "A": val_a or "—", "B": val_b or "—"})

    st.dataframe(pd.DataFrame(df_data), use_container_width=True)

    col1, col2, col3 = st.columns(3)
    
    score_a = cmp['offer_a']['score']
    score_b = cmp['offer_b']['score']
    best = cmp["best_offer"]
    
    with col1:
        st.metric("A Score", f"{score_a}/100", delta="Winner" if best == "A" else None)
    with col2:
        st.metric("B Score", f"{score_b}/100", delta="Winner" if best == "B" else None)
    with col3:
        if best == "Tie":
            st.metric("Result", "Tie")
        else:
            st.metric("Best", best, delta=f"+{abs(score_a - score_b)} pts")

            # ===================================================================
# CHATBOT - MOVED TO TOP
# ===================================================================
st.header("💬 Ask Questions About Your Contract")

if st.session_state.extracted:
    st.success("✅ Contract loaded! Ask me anything about it.")
    st.caption("🤖 **AI Model:** Llama 3.1 8B Instant (via Groq)")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("💭 Ask a question about your contract..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                context = {
                    "raw_text": st.session_state.extracted.get("raw_text", ""),
                    "extracted_fields": st.session_state.extracted.get("llm_structured_data_full", {}),
                    "question": prompt
                }
                
                chat_resp = api_post_json("/chat", context, timeout=60)
                
                if isinstance(chat_resp, dict) and chat_resp.get("error"):
                    error_msg = chat_resp.get("error", "")
                    if "401" in error_msg or "Invalid API Key" in error_msg:
                        response = "❌ **API Error:** Invalid Groq API key. Please check your `.env` file and ensure GROQ_API_KEY is set correctly."
                    else:
                        response = f"❌ **Error:** {error_msg}\n\nPlease check:\n1. Backend is running\n2. GROQ_API_KEY in .env file\n3. Internet connection"
                else:
                    try:
                        response = chat_resp.json().get("answer", "No response received.")
                    except:
                        response = "❌ Failed to parse response from backend."
                
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    if st.button("🗑️ Clear Chat", key="clear_chat_top"):
        st.session_state.chat_history = []
        st.rerun()
        
else:
    st.info("👆 Upload a contract PDF below to start asking questions")

st.markdown("---")

# ===================================================================
# FOOTER
# ===================================================================
st.markdown("---")
st.caption("Made with ❤️ | Backend: FastAPI + Groq | AI: Llama 3.1 8B Instant")