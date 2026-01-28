from flask import Blueprint, request, jsonify
from services.ocr_service import extract_text

upload_bp = Blueprint("upload", __name__, url_prefix="/api")

@upload_bp.route("/upload", methods=["POST"])
def upload_contract():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    text = extract_text(file)
    return jsonify({
        "message": "Contract uploaded",
        "extracted_text": text[:500]
    })
