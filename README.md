
# AI / LLM-Based Car Lease Contract Review and Negotiation Assistant

## Project Overview

This project implements an **AI / LLM-based system** that automatically analyzes **car lease contracts** and helps users understand them easily.
The system extracts important lease details, identifies risky clauses, suggests negotiation points, and generates a simple natural-language explanation using an **online open-source Large Language Model (LLM)**.

The project is designed as part of an **internship / academic project** and strictly follows the requirements provided in the project description PDF.

---

## Problem Statement

Car lease contracts are often long, complex, and written in legal or financial language.
Many users fail to identify unfavorable clauses such as high interest rates, penalties, or restrictive mileage limits.

Manual contract review is time-consuming and error-prone.
This project aims to automate the process and make car lease contracts **transparent and understandable** for users.

---

## Objectives

* Extract key information from car lease contracts automatically
* Identify risky or unfavorable clauses
* Provide negotiation recommendations
* Explain the contract in simple language using an LLM
* Generate structured and reliable output for analysis

---

## System Workflow

The project follows a step-by-step pipeline:

1. **PDF Ingestion**

   * Accepts car lease contracts in PDF format
   * Supports multi-page and scanned documents

2. **OCR (Optical Character Recognition)**

   * Converts PDF pages into images
   * Extracts text using **Tesseract OCR** (open-source)

3. **Text Preprocessing**

   * Combines and cleans OCR text
   * Prepares text for analysis

4. **Key Information Extraction**

   * Extracts:

     * Interest Rate (APR)
     * Monthly Payment
     * Down Payment
     * Residual Value
     * Mileage Allowance
     * VIN
     * Early Termination Fee
     * Contact Information (Email / Phone)

5. **Confidence Scoring**

   * Assigns confidence scores to extracted fields

6. **Risk Identification**

   * Detects risky terms such as:

     * High APR
     * High penalties
     * Low mileage limits

7. **Negotiation Recommendation**

   * Suggests what the user should negotiate based on risks

8. **LLM-Based Explanation**

   * Uses an **online open-source LLM via Groq API**
   * Generates a human-readable explanation of the contract
   * Explains risks and negotiation advice in simple language

9. **Structured Output**

   * Saves results in JSON format

---

## Technologies Used

* **Programming Language:** Python
* **OCR Engine:** Tesseract OCR
* **PDF Processing:** pdf2image, Pillow
* **LLM API:** Groq Free Inference API
* **LLM Model:** LLaMA-3.3-70B-Versatile (Text-to-Text)
* **Data Format:** JSON

---

## Project Structure

```
project-folder/
│
├── contract_extractor.py      # Main pipeline (OCR → extraction → negotiation → LLM)
├── llm_groq.py                # Groq API integration
├── test_pdf_to_img.py         # PDF to image conversion
├── page_0.png                 # OCR input images
├── page_1.png
├── extracted_contract.json    # Final output
├── README.md                  # Project documentation
```

---

## Dataset Description

Due to privacy and legal restrictions, real signed car lease contracts are not publicly available.

For this project:

* Publicly available lease templates were used
* Synthetic but realistic car lease contracts were generated
* Contract formats follow real-world lease agreements

This approach is widely accepted in academic and internship projects.

---

## Output Description

The system produces a structured JSON output containing:

* Extracted contract fields
* Confidence scores
* Identified risks
* Negotiation suggestions
* LLM-generated natural-language explanation

---

## How to Run the Project

1. Place the car lease PDF in the project folder
2. Convert PDF pages to images using `test_pdf_to_img.py`
3. Ensure `page_0.png`, `page_1.png`, etc. are generated
4. Add your **Groq API key** in `llm_groq.py`
5. Run the main pipeline:

   ```
   python contract_extractor.py
   ```
6. View the output in `extracted_contract.json`

---

## Project Status

✅ All modules specified in the project description have been implemented
✅ The system has been tested using sample lease contracts
✅ The project is **fully completed as per the provided PDF**

---

## Conclusion

This project demonstrates how OCR, rule-based extraction, and online open-source LLMs can be combined to automate contract analysis.
The system improves transparency, reduces manual effort, and helps users make informed decisions before signing a car lease contract.