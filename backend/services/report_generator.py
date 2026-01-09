from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import os
from typing import List, Dict, Optional


def generate_contract_report(
    contract_id: int,
    sla: Dict,
    fairness: Dict,
    vehicle_info: Optional[Dict]
) -> str:
    filename = f"contract_report_{contract_id}.pdf"
    output_path = os.path.join("reports", filename)

    os.makedirs("reports", exist_ok=True)

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    y = height - 50

    def draw(text: str):
        nonlocal y
        c.drawString(50, y, text)
        y -= 18
        if y < 60:
            c.showPage()
            y = height - 50

    def draw_section(title: str):
        draw(title)
        draw("-" * 45)

    def draw_list(title: str, items: List[str]):
        draw(title)
        if not items:
            draw("  - None identified")
        else:
            for item in items:
                draw(f"  - {item}")
        draw("")

    # ================= HEADER =================
    draw("CAR CONTRACT REVIEW REPORT")
    draw("=" * 50)
    draw(f"Contract ID: {contract_id}")
    draw(f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    draw("")

    # ================= SLA SUMMARY =================
    draw_section("SLA SUMMARY")
    draw(f"APR: {sla.get('apr', 'Unknown')} %")
    draw(f"Lease Term: {sla.get('lease_term', 'Unknown')} months")
    draw(f"Monthly Payment: ${sla.get('monthly_payment', 'Unknown')}")
    draw(f"Mileage Limit: {sla.get('mileage_limit', 'Unknown')} miles/year")
    draw("")

    # ================= VEHICLE INFORMATION =================
    draw_section("VEHICLE INFORMATION")
    if vehicle_info:
        for key, value in vehicle_info.items():
            draw(f"{key}: {value}")
    else:
        draw("Vehicle data not available")
    draw("")

    # ================= CONTRACT INSIGHTS =================
    draw_section("CONTRACT INSIGHTS (Pros & Cons)")

    draw_list("Pros", fairness.get("pros", []))
    draw_list("Cons", fairness.get("cons", []))
    draw_list("Negotiation Suggestions", fairness.get("suggestions", []))

    # ================= FOOTER =================
    draw("=" * 50)
    draw("This report is AI-assisted and intended for informational purposes only.")
    draw("Always consult a legal professional before signing any contract.")

    c.save()
    return output_path
