# report_generator.py

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import io


# ---------------------------------------------------------
#  PDF BUILDER (NO external fonts required)
# ---------------------------------------------------------

def build_comparison_pdf_bytes(meta: dict, summary: dict, compare: dict):
    """
    Generates a PDF in memory and returns the byte content.
    """

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    normal = styles["BodyText"]

    elements = []

    # -----------------------------------------------------
    # HEADER SECTION
    # -----------------------------------------------------
    report_title = meta.get("report_title", "Contract Comparison Report")
    elements.append(Paragraph(report_title, title_style))
    elements.append(Spacer(1, 0.2 * inch))

    # -----------------------------------------------------
    # SUMMARY SECTION
    # -----------------------------------------------------
    elements.append(Paragraph("<b>Contract Summary</b>", styles["Heading2"]))
    summary_text = summary.get("plain_summary", "No summary available.")
    elements.append(Paragraph(summary_text, normal))
    elements.append(Spacer(1, 0.2 * inch))

    # -----------------------------------------------------
    # OFFER COMPARISON TABLE
    # -----------------------------------------------------
    elements.append(Paragraph("<b>Offer Comparison</b>", styles["Heading2"]))

    offer_a = compare.get("offer_a", {})
    offer_b = compare.get("offer_b", {})

    fieldsA = offer_a.get("fields", {})
    fieldsB = offer_b.get("fields", {})

    table_data = [["Field", "Offer A", "Offer B"]]

    all_fields = sorted(set(list(fieldsA.keys()) + list(fieldsB.keys())))

    for key in all_fields:
        table_data.append([
            key,
            str(fieldsA.get(key, "—")),
            str(fieldsB.get(key, "—"))
        ])

    comparison_table = Table(table_data, colWidths=[2.6 * inch, 2.6 * inch, 2.6 * inch])
    comparison_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")
    ]))

    elements.append(comparison_table)
    elements.append(Spacer(1, 0.3 * inch))

    # -----------------------------------------------------
    # FAIRNESS SCORE TABLE
    # -----------------------------------------------------
    elements.append(Paragraph("<b>Fairness Scores</b>", styles["Heading2"]))

    fs_data = [
        ["Offer", "Score"],
        ["Offer A", str(offer_a.get("score", "N/A"))],
        ["Offer B", str(offer_b.get("score", "N/A"))]
    ]

    score_table = Table(fs_data, colWidths=[3 * inch, 3 * inch])
    score_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica")
    ]))

    elements.append(score_table)
    elements.append(Spacer(1, 0.3 * inch))

    # -----------------------------------------------------
    # BEST OFFER
    # -----------------------------------------------------
    best = compare.get("best_offer", "A")
    elements.append(Paragraph(f"<b>Recommended Offer: Offer {best}</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    # -----------------------------------------------------
    # NEGOTIATION TIPS
    # -----------------------------------------------------
    neg = compare.get("negotiation_tips", {})

    elements.append(Paragraph("<b>Negotiation Tips</b>", styles["Heading2"]))
    elements.append(Paragraph(f"<b>Polite:</b> {neg.get('polite', '—')}", normal))
    elements.append(Paragraph(f"<b>Firm:</b> {neg.get('firm', '—')}", normal))
    elements.append(Paragraph(f"<b>Legal-Based:</b> {neg.get('legal_based', '—')}", normal))

    elements.append(Spacer(1, 0.3 * inch))

    # -----------------------------------------------------
    # BUILD PDF
    # -----------------------------------------------------
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
