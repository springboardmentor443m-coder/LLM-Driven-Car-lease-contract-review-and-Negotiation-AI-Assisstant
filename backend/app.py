from flask import Flask, request, jsonify
import os

from ocr import extract_text
from llm_extract import extract_lease_details
from fairness_score import calculate_fairness
from vin_lookup import lookup_vin
from price_estimation import estimate_vehicle_price

app = Flask(__name__)

UPLOAD_FOLDER = "../uploads/contracts"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")

    if not file or file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # ---------------- SAVE FILE ----------------
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # ---------------- OCR ----------------
    extracted_text = extract_text(file_path)

    # ---------------- LLM EXTRACTION ----------------
    llm_json = extract_lease_details(extracted_text)
    if not isinstance(llm_json, dict):
        llm_json = {}

    # ---------------- FAIRNESS SCORE ----------------
    fairness = calculate_fairness(llm_json)

    # ---------------- VEHICLE DETAILS FROM PDF ----------------
    vehicle = llm_json.get("Vehicle", {})

    vin = vehicle.get("Vehicle_VIN")

    vin_details = {
        "VIN": vin,
        "Make": vehicle.get("Vehicle_Make"),
        "Model": vehicle.get("Vehicle_Model"),
        "Year": vehicle.get("Vehicle_Year"),
        "BodyClass": vehicle.get("Vehicle_Body_Type"),
        "FuelType": vehicle.get("Fuel_Type")
    }

    # ---------------- VIN WEBSITE FALLBACK ----------------
    if vin:
        api_data = lookup_vin(vin)
        for key in vin_details:
            if not vin_details[key]:
                vin_details[key] = api_data.get(key)

    # ---------------- PRICE ESTIMATION (FIXED) ----------------
    estimated_vehicle_price = {
        "below_market_price": None,
        "average_market_price": None,
        "above_market_price": None,
        "confidence": None
    }

    mileage = llm_json.get("Mileage_Limit")

    if vin and mileage:
        try:
            estimated_vehicle_price = estimate_vehicle_price(
                vin=vin,
                mileage=int(mileage)
            )
        except Exception as e:
            print("PRICE ESTIMATION ERROR:", e)

    # ---------------- FINAL RESPONSE ----------------
    return jsonify({
        "file_name": file.filename,
        "extracted_details": llm_json,
        "vin_details": vin_details,
        "estimated_vehicle_price": estimated_vehicle_price,
        "fairness_score": fairness
    })


if __name__ == "__main__":
    app.run(debug=True)
