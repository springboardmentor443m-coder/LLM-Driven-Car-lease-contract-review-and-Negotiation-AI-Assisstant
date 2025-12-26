from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app
import re

from app.state import state
from app.services.ocr_service import image_ocr, pdf_ocr
from app.services.llm_service import base_llm, chat_llm
from app.services.vehicle_db_service import get_vehicle_specs
from app.services.nhtsa_service import get_recalls
from app.services.market_service import get_market_price
from app.services.valuation_service import evaluate_deal, estimate_5yr_value

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

main = Blueprint("main", __name__)

# -------------------------------
# SMART MAKE / MODEL EXTRACTION
# -------------------------------
def extract_make_model(text: str):
    text = text.lower()

    makes = [
        "porsche", "bmw", "audi", "mercedes", "toyota",
        "honda", "ford", "chevrolet", "tesla", "volkswagen"
    ]

    models = [
        "cayenne", "x5", "x3", "a4", "a6", "civic",
        "camry", "mustang", "model s", "model 3"
    ]

    found_make = "Unknown"
    found_model = "Unknown"

    for m in makes:
        if m in text:
            found_make = m.capitalize()
            break

    for mdl in models:
        if mdl in text:
            found_model = mdl.capitalize()
            break

    return found_make, found_model


def extract_price(text, label):
    match = re.search(rf"{label}.*?\$([\d,]+)", text, re.IGNORECASE)
    return int(match.group(1).replace(",", "")) if match else 0


# -------------------------------
# ROUTES
# -------------------------------
@main.route("/")
def upload():
    return render_template("upload.html")


@main.route("/ocr", methods=["POST"])
def ocr():
    file = request.files["file"]

    if file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        image_ocr(file, current_app.config["TESSERACT_PATH"])
    else:
        pdf_ocr(file, current_app.config["TESSERACT_PATH"])

    return redirect(url_for("main.process"))


@main.route("/process")
def process():
    # ---------------- VIN ----------------
    vin_match = re.search(r"\b[A-HJ-NPR-Z0-9]{17}\b", state.raw_text)
    state.vin = vin_match.group(0) if vin_match else ""

    # ---------------- SUMMARY ----------------
    llm = base_llm(current_app.config["GROQ_API_KEY"])
    state.summary = llm.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": state.raw_text}]
    ).choices[0].message.content

    # ---------------- VEHICLE SPECS ----------------
    api_specs = {}
    if state.vin:
        api_specs = get_vehicle_specs(
            state.vin,
            current_app.config["RAPIDAPI_KEY"]
        )

    pdf_make, pdf_model = extract_make_model(state.raw_text)

    make = api_specs.get("make") or pdf_make
    model = api_specs.get("model") or pdf_model
    year = api_specs.get("year") or "Unknown"

    state.vehicle_specs = {
        "make": make,
        "model": model,
        "year": year
    }

    # ---------------- RECALLS ----------------
    state.recalls = get_recalls(make, model, year)

    # ---------------- MARKET PRICES ----------------
    market = get_market_price(
        make, model, year,
        current_app.config["RAPIDAPI_KEY"]
    )

    dealer_price = market.get("asking_price", 0)
    market_avg = market.get("average_price", 0)

    if dealer_price == 0:
        dealer_price = extract_price(state.raw_text, "asking")

    if market_avg == 0:
        market_avg = extract_price(state.raw_text, "market")

    # ---------------- DEAL EVALUATION ----------------
    state.deal_analysis = evaluate_deal(dealer_price, market_avg)
    state.resale_5yr = estimate_5yr_value(market_avg)

    # ---------------- RAG CONTEXT ----------------
    rag_context = f"""
VEHICLE DETAILS
Make: {make}
Model: {model}
Year: {year}

PRICING
Dealer Asking Price: ${dealer_price}
Market Average Price: ${market_avg}

DEAL ANALYSIS
Verdict: {state.deal_analysis['verdict']}
Deal Score: {state.deal_analysis['deal_score']}/100
Fair Buy Price Range: {state.deal_analysis['fair_price_range']}
Price Difference: {state.deal_analysis['price_difference_percent']}%

5-YEAR VALUE ESTIMATE
{state.resale_5yr}

RECALL INFORMATION
{state.recalls}
"""

    docs = [Document(page_content=rag_context)]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceBgeEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
    )

    state.vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    return redirect(url_for("main.assistant"))


@main.route("/assistant")
def assistant():
    return render_template("assistant.html")


@main.route("/chat_process", methods=["POST"])
def chat_process():
    question = request.form.get("user_question")

    retriever = state.vectorstore.as_retriever()
    docs = retriever.invoke(question)

    context = "\n".join(d.page_content for d in docs)

    llm = chat_llm(current_app.config["GROQ_API_KEY"])

    response = llm.invoke(
        f"""
You are an AI car lease and purchase negotiation assistant.
Answer ONLY using the context below.
Be confident, numeric, and decisive.

Context:
{context}

Question:
{question}
"""
    )

    return jsonify({
        "chat_history": [
            {"role": "user", "text": question},
            {"role": "bot", "text": response.content}
        ]
    })
