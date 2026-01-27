


from flask import Flask, request, jsonify
from flask_cors import CORS

from services.ocr_service import extract_text
from services.llm_service import extract_sla_from_contract

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Car Lease Contract Review AI Backend is running"
    })


