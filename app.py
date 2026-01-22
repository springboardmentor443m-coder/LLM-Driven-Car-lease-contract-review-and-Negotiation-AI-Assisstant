from flask import Flask, render_template, redirect, url_for, request, jsonify
from PIL import Image
import pytesseract
import fitz
import io
import os
import requests

from groq import Groq
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_core.documents import Document
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_core.prompts import PromptTemplate


app = Flask(__name__)

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\anisr\OneDrive\Desktop\bin\tesseract.exe"

groq_raw = Groq(api_key="groq_key")

llm = ChatGroq(
    groq_api_key="groq_key",
    model_name="llama-3.3-70b-versatile",
    temperature=0.4
)

chat_llm = ChatGroq(
    groq_api_key="groq_key",
    model_name="llama-3.3-70b-versatile",
    temperature=0.4
)

# ======================================================
#   GLOBALS
# ======================================================
car1_text = ""
car2_text = ""
compare_vectorstore = None
car1_summary = ""
car2_summary = ""
car1_market = ""
car2_market = ""

final_text = ""
vin = ""
summary_text = ""
mileage = ""
Make = ""
Model = ""
ModelYear = ""
recall_summary = ""
market_values = ""
extracted_details = ""
prior_info = ""
rd_flgs=""

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
compare_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def image_ocr(file):
    global final_text
    img = Image.open(file)
    final_text = pytesseract.image_to_string(img)

def pdf_ocr(file):
    global final_text
    temp_path = "temp.pdf"
    with open(temp_path, "wb") as f:
        f.write(file.read())

    try:
        pdf = fitz.open(temp_path)
        for page in pdf:
            pix = page.get_pixmap()
            img = Image.open(io.BytesIO(pix.tobytes()))
            final_text += pytesseract.image_to_string(img)
    finally:
        pdf.close()
        if os.path.exists(temp_path):
            os.remove(temp_path)


def get_market_value(vin, mileage):
    url = "https://vehicle-pricing-api.p.rapidapi.com/1837/get%2Bvehicle%2Bprice%2Bdata"

    querystring = {"vin":vin,"mileage":mileage}

    headers = {
        "x-rapidapi-key": "vehicle-pricing-api-key",
        "x-rapidapi-host": "vehicle-pricing-api.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    data = response.json()

    prices = data["data"].get("prices", {})
    return {
        "vin": data["data"].get("vin"),
        "vehicle": data["data"].get("vehicle"),
        "price_type": data["data"].get("type"),
        "below_market_price": prices.get("below"),
        "average_market_price": prices.get("average"),
        "above_market_price": prices.get("above"),
        "certainty_percent": data["data"].get("certainty"),
        "sample_size": data["data"].get("count"),
        "price_period": data["data"].get("period")
    }

@app.route('/')
def primary():
    return render_template('home.html')


@app.route('/ocr', methods=['POST', 'GET'])
def ocr():
    global final_text
    final_text = ""

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        pdf_ocr(file)
    else:
        image_ocr(file)

    return redirect(url_for("ocr_summary"))


@app.route('/ocr_summary')
def ocr_summary():
    global summary_text, vin, mileage

    summary_text = llm.invoke(
        f"Summarize vehicle lease/loan agreement: {final_text}"
    ).content

    vin = llm.invoke(
        f"Extract VIN only (17 chars) from: {summary_text}"
    ).content[-17:]

    mileage = llm.invoke(
        f"Extract mileage (digits only, no commas/units) from: {summary_text}"
    ).content.strip()

    return redirect(url_for("red_flags"))

@app.route('/red_flags')
def red_flags():
    global rd_flgs,summary_text
    rd_flgs=llm.invoke(f"Provide some red flags present in agreement using the following information {summary_text} in bullet points.").content.strip()
    return redirect(url_for("vin_decode"))

@app.route('/vin_decode')
def vin_decode():
    
    global extracted_details, Make, Model, ModelYear, mileage

    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json"
    response = requests.get(url).json()
    res = response.get("Results", [{}])[0]

    extracted_details = {
        "Make": res.get("Make"),
        "Model": res.get("Model"),
        "ModelYear": res.get("ModelYear"),
        "Trim": res.get("Trim"),
        "FuelType": res.get("FuelTypePrimary"),
        "BodyType": res.get("BodyClass"),
        "Mileage": mileage
    }

    Make = res.get("Make")
    Model = res.get("Model")
    ModelYear = res.get("ModelYear")

    return redirect(url_for("recalls"))


@app.route("/recalls")
def recalls():
    global recall_summary, Make, Model, ModelYear

    url = f"https://api.nhtsa.gov/recalls/recallsByVehicle?make={Make}&model={Model}&modelYear={ModelYear}"
    recalls = requests.get(url).json().get("results", [])

    if not recalls:
        recall_summary = "No recalls reported."
    else:
        raw = "\n".join([r.get("Summary", "") for r in recalls])
        recall_summary = llm.invoke(f"Summarize these recalls: {raw}").content

    return redirect(url_for("market_pred"))


@app.route("/market_pred")
def market_pred():
    global market_values
    market_values = get_market_value(vin, mileage)
    return redirect(url_for("process"))


@app.route("/process", methods=["GET"])
def process():
    global prior_info, vectorstore

    prior_info = f"""
Agreement Summary:
{summary_text}

Vehicle Details:
{extracted_details}

red flags:
{rd_flgs}

Recall Info:
{recall_summary}

Market Pricing:
{market_values}
"""

    docs = [Document(page_content=prior_info)]
    chunks = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50).split_documents(docs)

    embeddings = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    vectorstore = FAISS.from_documents(chunks, embeddings)

    return jsonify({
        "summary": summary_text,
        "car_details": extracted_details,
        "recall_summary": recall_summary,
        "market_price": market_values,
        "red_flags":rd_flgs
    })


@app.route("/chat")
def chat():
    return render_template("chat.html")


@app.route("/chat_process", methods=["POST"])
def chat_process():
    user_q = request.form.get("user_question")

    qa_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
ANSWER BASED ON CONTEXT.
If missing, use general knowledge.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=chat_llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": qa_prompt},
        verbose=False
    )

    result = chain.invoke({"question": user_q})

    return jsonify({
        "answer": result["answer"],
        "chat_history": [
            {"role": "user" if i % 2 == 0 else "assistant", "text": m.content}
            for i, m in enumerate(result["chat_history"])
        ]
    })

@app.route("/compare")
def compare():
    return render_template("compare.html")


@app.route("/compare_upload", methods=["POST"])
def compare_upload():
    global car1_text, car2_text, final_text

    file1 = request.files.get("car1")
    file2 = request.files.get("car2")

    final_text = ""
    pdf_ocr(file1) if file1.filename.lower().endswith(".pdf") else image_ocr(file1)
    car1_text = final_text

    final_text = ""
    pdf_ocr(file2) if file2.filename.lower().endswith(".pdf") else image_ocr(file2)
    car2_text = final_text

    return redirect(url_for("compare_process"))


@app.route("/compare_process")
def compare_process():
    global compare_vectorstore

    car1_summary = llm.invoke(f"Summarize vehicle agreement: {car1_text}").content
    car2_summary = llm.invoke(f"Summarize vehicle agreement: {car2_text}").content

    car1_vin = llm.invoke(f"Extract VIN (17 chars only) from: {car1_text}").content[-17:]
    car2_vin = llm.invoke(f"Extract VIN (17 chars only) from: {car2_text}").content[-17:]

    car1_mileage = llm.invoke(f"Extract mileage digits only from: {car1_text}").content.strip()
    car2_mileage = llm.invoke(f"Extract mileage digits only from: {car2_text}").content.strip()

    car1_market = get_market_value(car1_vin, car1_mileage)
    car2_market = get_market_value(car2_vin, car2_mileage)

    recommendation = llm.invoke(f"""
Compare Car 1 vs Car 2 and recommend best deal.
CAR1 SUMMARY: {car1_summary}
CAR1 MARKET: {car1_market}
CAR2 SUMMARY: {car2_summary}
CAR2 MARKET: {car2_market}
Respond in:
Recommendation: <decision>
Reasons: <bullet points>
""").content

    ctx = f"""
CAR1 SUMMARY: {car1_summary}
CAR1 MARKET: {car1_market}

CAR2 SUMMARY: {car2_summary}
CAR2 MARKET: {car2_market}

RECOMMENDATION:
{recommendation}
"""

    docs = [Document(page_content=ctx)]
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(docs)
    embeddings = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-en-v1.5")

    compare_vectorstore = FAISS.from_documents(chunks, embeddings)

    return jsonify({
        "recommendation": recommendation,
        "status": "Comparison completed"
    })


@app.route("/chat_abt_two")
def chat_abt_two():
    return render_template("chat_two.html")


@app.route("/compare_chat", methods=["POST"])
def compare_chat():
    user_q = request.form.get("user_question")

    compare_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
Use CONTEXT to answer vehicle comparison questions.
If missing, use automotive knowledge.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=chat_llm,
        retriever=compare_vectorstore.as_retriever(search_kwargs={"k": 4}),
        memory=compare_memory,
        combine_docs_chain_kwargs={"prompt": compare_prompt},
        verbose=False
    )

    result = chain.invoke({"question": user_q})

    return jsonify({
        "answer": result["answer"],
        "chat_history": [
            {"role": "user" if i % 2 == 0 else "assistant", "text": m.content}
            for i, m in enumerate(result["chat_history"])
        ]
    })


if __name__ == "__main__":
    app.run()
