from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
import os


def generate_contract_report(
    contract_id: int,
    sla: dict,
    fairness: dict,
    vehicle_info: dict | None
) -> str:
    filename = f"contract_report_{contract_id}.pdf"
    output_path = os.path.join("reports", filename)

    os.makedirs("reports", exist_ok=True)

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    y = height - 50

    def draw(text):
        nonlocal y
        c.drawString(50, y, text)
        y -= 18
        if y < 60:
            c.showPage()
            y = height - 50

    # ---------------- HEADER ----------------
    draw("CAR CONTRACT ANALYSIS REPORT")
    draw("=" * 50)
    draw(f"Contract ID: {contract_id}")
    draw(f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    draw("")

    # ---------------- SLA ----------------
    draw("SLA SUMMARY")
    draw("-" * 40)
    draw(f"APR: {sla.get('apr')} %")
    draw(f"Lease Term: {sla.get('lease_term')} months")
    draw(f"Monthly Payment: ${sla.get('monthly_payment')}")
    draw(f"Mileage Limit: {sla.get('mileage_limit')} miles/year")
    draw("")

    # ---------------- VEHICLE ----------------
    draw("VEHICLE INFORMATION")
    draw("-" * 40)
    if vehicle_info:
        for k, v in vehicle_info.items():
            draw(f"{k}: {v}")
    else:
        draw("Vehicle data not available")
    draw("")

    # ---------------- FAIRNESS ----------------
    draw("FAIRNESS & RISK ANALYSIS")
    draw("-" * 40)
    draw(f"Fairness Score: {fairness.get('fairness_score')} / 100")
    draw(f"Risk Level: {fairness.get('risk_level')}")
    draw("")

    if fairness.get("risk_factors"):
        draw("Risk Factors:")
        for r in fairness["risk_factors"]:
            draw(f"- {r}")
    else:
        draw("No major risks detected")

    draw("")
    draw("Negotiation Advice:")
    for s in fairness.get("negotiation_advice", []):
        draw(f"- {s}")

    c.save()
    return output_path
