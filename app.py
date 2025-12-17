from flask import Flask,render_template,redirect,url_for,request,jsonify
from groq import Groq
from PIL import Image
import pytesseract
import fitz
import io
import os
import requests
from groq import Groq




app=Flask(__name__)

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\anisr\OneDrive\Desktop\bin\tesseract.exe"

llm = Groq(api_key="groq_api_key")



final_text = ""
vin = ""
summary_text=""
mileage=""
Make=""
Model=""
ModelYear=""
recall_summary=""
market_values=""
extracted_details=""

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


def get_market_value(vin,mileage):
    url = "https://vehicle-pricing-api.p.rapidapi.com/1837/get%2Bvehicle%2Bprice%2Bdata"

    querystring = {"vin":vin,"mileage":mileage}

    headers = {
        "x-rapidapi-key": "vehicle_pricing_api_key",
        "x-rapidapi-host": "vehicle-pricing-api.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    
    data=response.json()
    
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

@app.route('/ocr', methods=['POST',"GET"])
def ocr():
    global final_text
    final_text = ""

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = file.filename.lower()

    if filename.endswith((".png", ".jpg", ".jpeg")):
        image_ocr(file)
    elif filename.endswith(".pdf"):
        pdf_ocr(file)
    else:
        return jsonify({"error": "Unsupported file type"}), 400

    return redirect(url_for("ocr_summary"))

    
@app.route('/ocr_summary')
def ocr_summary():
    query = f"""Generate a summary from the content provided below.
    Include the following details if present:
    vehicle number, Interest rate, APR, Lease term duration, Monthly payment,
    Down payment, Residual value, Mileage allowance & overage charges,
    Early termination clause, Purchase option (buyout price),
    Maintenance responsibilities, Warranty and insurance coverage,
    Penalties or late fee clauses.

    Now fill the values based ONLY on the OCR text below.

    information: {final_text}"""

    response = llm.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": query}],
        max_tokens=1000
    )

    global summary_text, vin, mileage
    
    summary_text = response.choices[0].message.content

    query_vin = f"Provide the VIN using the information provided. Information: {summary_text}. Don't give any text other than vin.Don't even mention it as extracted vin"
    response_vin = llm.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": query_vin}],
        max_tokens=100
    )
    raw_vin = response_vin.choices[0].message.content.strip()
    vin=raw_vin[-17:]
    
    query_2= f"Provide the mileage using the information provided. Information: {summary_text}. Don't give any text other than mileage.Don't even mention the units.Do not give any commas in the figure just simply gave a number."
    ml = llm.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": query_2}],
        max_tokens=100
    )
    mileage=ml.choices[0].message.content.strip()
    
    return redirect(url_for("vin_decode"))

@app.route("/vin_decode")
def vin_decode():
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json"

    response = requests.get(url).json()


    result = response.get("Results", [{}])[0]
    
    global extracted_details, Make, Model, ModelYear
    


    extracted_details = {
        "Model": result.get("Model") or None,
        "Make": result.get("Make") or None,
        "ModelYear": result.get("ModelYear") or None,
        "Trim": result.get("Trim") or None,
        "FuelType": result.get("FuelTypePrimary") or None,
        "BodyType": result.get("BodyClass") or None,
        "Mileage":mileage
    }
    
    Make=result.get("Make")
    Model=result.get("Model")
    ModelYear=result.get("ModelYear")
    
    return redirect(url_for("recalls"))

@app.route("/recalls")
def recalls():
    
    global Make,Model,ModelYear
    
    nhtsa_url = f"https://api.nhtsa.gov/recalls/recallsByVehicle?make={Make}&model={Model}&modelYear={ModelYear}"
    response = requests.get(nhtsa_url).json()
    recalls=response.get("results", [])

    recall_text = ""

    if recalls:
        for idx, rec in enumerate(recalls, start=1):
            recall_text += f"""
    Recall {idx}:
    Campaign Number: {rec.get('NHTSACampaignNumber')}
    Summary: {rec.get('Summary')}
    Consequence: {rec.get('Consequence')}
    Remedy: {rec.get('Remedy')}
    -----------------------------------
    """
    else:
        recall_text = "No recalls reported for this vehicle."
        

    recall_summary_prompt=f"Summarize the recalls provided to you.  Recalls : {recall_text}"
    
    
    recall_summary_response = llm.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": recall_summary_prompt}],
        max_tokens=500
    )
    global recall_summary
    
    recall_summary = recall_summary_response.choices[0].message.content
    return redirect(url_for("market_pred"))

@app.route("/market_pred")
def market_pred():
    
    global market_values
    market_values = get_market_value(vin, mileage)
    
    return redirect(url_for("process"))



@app.route("/process", methods=["POST","GET"])
def process():
    return jsonify({
        "summary": summary_text,
        "car_details":extracted_details,
        "recall_summary":recall_summary,
        "market_price": market_values
        
    })
    
    
@app.route("/chatbot")
def chatbot():
    return render_template("chat.html")

if __name__ == "__main__":  
    app.run()
    
    
