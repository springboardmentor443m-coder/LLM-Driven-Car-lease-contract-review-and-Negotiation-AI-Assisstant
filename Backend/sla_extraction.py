from flask import Blueprint, jsonify

sla_bp = Blueprint("sla", __name__, url_prefix="/api")

@sla_bp.route("/extract-sla", methods=["GET"])
def extract_sla():
    return jsonify({
        "APR": "8.5%",
        "Lease Term": "36 months",
        "Monthly Payment": "$420",
        "Mileage Limit": "12,000/year",
        "Early Termination": "Penalty applies"
    })
