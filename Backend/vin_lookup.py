from flask import Blueprint, jsonify, request

vin_bp = Blueprint("vin", __name__, url_prefix="/api")

@vin_bp.route("/vin", methods=["GET"])
def vin_lookup():
    vin = request.args.get("vin")
    return jsonify({
        "VIN": vin,
        "Make": "Toyota",
        "Model": "Camry",
        "Year": 2021,
        "Recalls": "None"
    })
