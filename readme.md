
                     AI / LLM-Based Car Lease Contract Review, Comparison, and Chatbot Assistant

## 📌 Project Overview

This project is an AI-powered system designed to **analyze car lease contracts**, help users **understand complex lease terms**, **identify risks**, and **compare multiple contracts** before making a decision.

The system supports both **text-based and scanned PDF lease agreements**. It automatically extracts key lease information using OCR, generates **human-readable explanations** using a Large Language Model (LLM), and provides an **interactive chatbot** for contract-related queries. A modern web interface allows users to upload and analyze **multiple contracts simultaneously**.

---

## 🎯 Project Objectives

* Simplify complex car lease contracts for users
* Extract key lease details automatically from PDF documents
* Support scanned and image-based lease agreements
* Identify risky or unfavorable contract clauses
* Provide negotiation suggestions for better lease terms
* Enable comparison of multiple lease contracts
* Offer an intelligent chatbot for contract-related questions
* Present insights in clear, easy-to-understand language

---

## ⚙️ System Pipeline

1. **PDF Upload**
   Users upload one or more car lease contracts in PDF format through the web interface.

2. **PDF to Image Conversion**
   Each page of the uploaded PDFs is converted into images to support OCR processing.

3. **OCR (Optical Character Recognition)**
   Tesseract OCR extracts text from the images, enabling support for scanned contracts.

4. **Text Preprocessing**
   Extracted text is cleaned and combined for further analysis.

5. **Contract Information Extraction**
   Rule-based logic extracts important lease details such as:

   * Monthly payment
   * Interest rate (APR)
   * Down payment
   * Mileage allowance
   * Residual value
   * Early termination fees

6. **Confidence Scoring**
   Each extracted field is assigned a confidence score based on extraction reliability.

7. **Risk Identification**
   The system flags potentially risky clauses such as high interest rates, low mileage limits, or high penalties.

8. **Negotiation Suggestions**
   Actionable negotiation suggestions are generated based on detected risks.

9. **LLM-Based Explanation**
   An LLM (via Groq API) generates a **concise, human-readable summary** explaining the contract, costs, and risks.

10. **Multi-Contract Comparison**
    When multiple contracts are uploaded, the system generates a comparison table highlighting key differences.

11. **Chatbot Interaction**
    Users can interactively ask questions about one or multiple analyzed contracts using a chatbot.

---

## 🤖 Chatbot Features

* Answers questions strictly based on extracted contract data and AI explanations
* No use of external or internet-based knowledge
* Context-aware and contract-grounded responses
* Supports multi-contract comparison queries

Example questions:

* “Is this contract risky?”
* “Which contract is better?”
* “What should I negotiate in this lease?”
* “Compare mileage limits across contracts”
* “Explain the APR in simple terms”

---

## 📄 Output Generated

* **Structured JSON files** containing:

  * Extracted lease details
  * Confidence scores
  * Identified risks
  * Negotiation suggestions
* **Human-readable AI summaries** of each contract
* **Comparison tables** for multiple contracts
* **Interactive chatbot responses**

---

## 🛠️ Technologies Used

* Python
* Tesseract OCR
* PDF2Image
* Pillow
* Streamlit (Web Interface)
* Groq API (Open-source LLM)
* JSON
* Pandas

---

## 📁 Project Structure

```
INFOSYS_INTERNSHIP2/
│
├── app.py                     # Streamlit web application (UI + chatbot)
├── chatbot.py                 # Chatbot prompt and conversation logic
├── contract_extractor.py      # OCR and contract information extraction
├── contract_explainer.py      # LLM-based contract explanation logic
├── llm_groq.py                # Groq API integration
│
├── extracted_contract.json    # Sample extracted contract output
├── llm_explanation.json       # Sample LLM explanation output
│
├── uploaded_pdfs/             # User-uploaded PDF contracts
├── page_images/               # Images generated from PDFs
├── sample_datasets/           # Sample lease PDFs for testing
│
├── test_pdf_to_img.py         # PDF to image conversion test
├── test_ocr.py                # OCR testing script
│
├── .env                       # Environment variables (API keys)
├── README.md
```

---

## ▶️ How to Run the Project

### Step 1: Install Dependencies

```bash
pip install pytesseract pillow pdf2image streamlit pandas requests
```

Ensure **Tesseract OCR** is installed and added to the system PATH.

---

### Step 2: Set Up Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

### Step 3: Run the Web Application

```bash
streamlit run app.py
```

Open the application in your browser:

```
http://localhost:8501
```

---

## 🌍 Real-World Use Case

A customer receives one or more car lease agreements from different dealers and is unsure which offer is better or whether there are hidden risks.
By uploading the contracts to this system, the customer can quickly:

* Understand key lease terms
* Identify financial risks
* Compare multiple offers
* Ask questions through an AI chatbot
* Make a more informed decision before signing

---

## 🚫 Scope Clarification

* ✔ Focuses on contract understanding, comparison, and negotiation support
* ❌ Does not predict car resale prices
* ❌ Does not calculate vehicle depreciation
* ❌ Does not replace legal professionals

---

## 🔮 Future Enhancements

* Support for additional contract types (insurance, loans)
* Advanced risk scoring and visualization
* Exportable comparison reports (PDF)
* Improved UI animations and analytics
* Deployment on cloud platforms

---

## 👤 Author

**Rohith V**
B.Tech – Computer Science (AI & ML)