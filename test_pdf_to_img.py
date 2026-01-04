from pdf2image import convert_from_path

pdf_path = r"E:\INFOSYS_INTERNSHIP2\sample1.pdf"

pages = convert_from_path(
    pdf_path,
    dpi=300,
    poppler_path=r"C:\Release-25.11.0-0\poppler-25.11.0\Library\bin"
)

for i, page in enumerate(pages):
    output_path = f"page_{i}.png"
    page.save(output_path, "PNG")
    print("Saved:", output_path)
