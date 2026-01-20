from flask import Flask, request, render_template, jsonify
import os

from ocr import extract_text
from llm_extract import extract_lease_details
from fairness_score import calculate_fairness
from vin_lookup import lookup_vin
from price_estimation import estimate_vehicle_price
from chatbot import answer_question

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

UPLOAD_FOLDER = "../uploads/contracts"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- GLOBAL MEMORY ----------------
LAST_RESULT = {}
CHAT_HISTORY = []


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- UPLOAD & ANALYZE ----------------
@app.route("/upload", methods=["POST"])
def upload():
    global LAST_RESULT, CHAT_HISTORY
    CHAT_HISTORY = []  # reset chat on new upload

    file = request.files.get("file")
    if not file or file.filename == "":
        return "No file selected"

    # Save file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # OCR
    extracted_text = extract_text(file_path)

    # LLM Extraction
    llm_json = extract_lease_details(extracted_text)
    if not isinstance(llm_json, dict):
        llm_json = {}

    # Fairness
    fairness = calculate_fairness(llm_json)

    lease = llm_json.get("Lease", {})
    vehicle = llm_json.get("Vehicle", {})

    # VIN Details
    vin_details = {
        "VIN": vehicle.get("Vehicle_VIN"),
        "Make": vehicle.get("Vehicle_Make"),
        "Model": vehicle.get("Vehicle_Model"),
        "Year": vehicle.get("Vehicle_Year"),
        "BodyClass": vehicle.get("Vehicle_Body_Type"),
        "FuelType": vehicle.get("Fuel_Type")
    }

    # VIN API fallback
    if vin_details["VIN"]:
        api_data = lookup_vin(vin_details["VIN"])
        for k in vin_details:
            if not vin_details[k]:
                vin_details[k] = api_data.get(k)

    # Price Estimation
    estimated_vehicle_price = {}
    mileage = lease.get("Mileage_Limit")

    if vin_details["VIN"] and mileage:
        try:
            estimated_vehicle_price = estimate_vehicle_price(
                vin=vin_details["VIN"],
                mileage=int("".join(filter(str.isdigit, str(mileage))))
            )
        except:
            estimated_vehicle_price = {}

    # Save for chatbot
    LAST_RESULT = {
        "lease": lease,
        "vin": vin_details,
        "fairness": fairness
    }

    return render_template(
        "result.html",
        extracted_details=llm_json,
        vin_details=vin_details,
        estimated_vehicle_price=estimated_vehicle_price,
        fairness_score=fairness
    )


# ---------------- CHATBOT PAGE ----------------
@app.route("/chatbot")
def chatbot_page():
    return render_template("chatbot.html")


# ---------------- CHAT PROCESS (FOR YOUR UI) ----------------
@app.route("/chat_process", methods=["POST"])
def chat_process():
    global CHAT_HISTORY, LAST_RESULT

    question = request.form.get("user_question", "").strip()
    if not question:
        return jsonify({"chat_history": CHAT_HISTORY})

    # User message
    CHAT_HISTORY.append({
        "role": "user",
        "text": question
    })

    # ✅ IMPORTANT FIX
    if not LAST_RESULT:
        reply = "Please upload a contract first."
    else:
        reply = answer_question(question, LAST_RESULT)

    # Bot message
    CHAT_HISTORY.append({
        "role": "bot",
        "text": reply
    })

    return jsonify({"chat_history": CHAT_HISTORY})


if __name__ == "__main__":
    app.run(debug=True)