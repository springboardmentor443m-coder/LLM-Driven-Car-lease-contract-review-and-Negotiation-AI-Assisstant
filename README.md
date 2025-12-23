                        AI / LLM-Based Car Lease Contract Review and Chatbot Assistant

## 📌 Project Overview

This project is an AI-based system designed to analyze car lease contracts and help users understand them before signing.  
It automatically extracts important lease terms, identifies potential risks, provides negotiation suggestions, and allows users to interact with the contract through an intelligent chatbot.

The system works on both text-based and scanned PDF lease agreements and generates clear, easy-to-understand explanations using a Large Language Model (LLM).

---

## 🎯 Project Objectives

- Simplify complex car lease contracts for users
- Extract key lease details automatically from PDFs
- Identify risky or unfavorable contract terms
- Suggest negotiation points
- Provide an interactive chatbot for contract-related questions
- Ensure explanations are clear, accurate, and contract-grounded

---

## ⚙️ System Pipeline

1. **PDF Input**  
   User uploads a car lease contract in PDF format.

2. **PDF to Image Conversion**  
   Each page of the PDF is converted into images for OCR processing.

3. **OCR (Optical Character Recognition)**  
   Tesseract OCR extracts text from the images, supporting scanned documents.

4. **Text Preprocessing**  
   Extracted text is cleaned and combined for analysis.

5. **Contract Information Extraction**  
   Rule-based logic is used to extract important lease details such as:
   - Monthly payment  
   - Interest rate (APR)  
   - Down payment  
   - Mileage allowance  
   - Residual value  
   - Early termination fees  

6. **Confidence Scoring**  
   Each extracted field is assigned a confidence score.

7. **Risk Identification**  
   The system flags potentially risky clauses like high interest rates or penalties.

8. **Negotiation Suggestions**  
   Suggestions are generated to help users negotiate better lease terms.

9. **LLM-Based Explanation**  
   An LLM (via Groq API) explains the contract and risks in simple language.

10. **Chatbot Interaction**  
    Users can ask questions about the analyzed contract and receive context-aware answers.

---

## 🤖 Chatbot Features

- Answers questions strictly based on extracted contract data
- Does not use external or internet-based information
- Supports natural, conversational interaction

### Chatbot Enhancements

- **Intent-Aware Responses (Level 2)**  
  Detects whether the user is asking about risks, negotiation, summary, or specific clauses and adapts responses accordingly.

- **Conversation Memory (Level 3)**  
  Remembers recent questions and answers to handle follow-up queries smoothly.

Example questions:
- “Is this contract risky?”
- “What should I negotiate?”
- “Explain the mileage clause”
- “Why is the interest rate a problem?”

---

## 📄 Output Generated

- Structured JSON file containing:
  - Extracted lease details
  - Confidence scores
  - Identified risks
  - Negotiation suggestions
- Plain-language explanations of the contract
- Interactive chatbot responses

---

## 🛠️ Technologies Used

- Python
- Tesseract OCR
- PDF2Image
- Pillow
- Flask (for web-based chatbot)
- Groq API (Open-source LLM)
- JSON

---

## 📁 Project Structure

```

├── contract_extractor.py      # OCR and contract information extraction
├── chatbot.py                 # Chatbot logic (intent + memory)
├── run_chatbot.py             # Terminal-based chatbot
├── app.py                     # Web-based chatbot (Flask)
├── test_pdf_to_img.py         # PDF to image conversion
├── test_ocr.py                # OCR testing script
├── extracted_contract.json    # Extracted contract output
├── sample_datasets/           # Sample car lease PDFs
├── templates/
│   └── index.html             # Chatbot web interface
├── README.md
├── .gitignore

````

---

## ▶️ How to Run the Project

### Step 1: Install Dependencies
```bash
pip install pytesseract pillow pdf2image flask requests
````

Ensure Tesseract OCR is installed and added to system PATH.

### Step 2: Run Contract Analysis

```bash
python contract_extractor.py
```

### Step 3: Run Terminal Chatbot

```bash
python run_chatbot.py
```

### Step 4: Run Web Chatbot

```bash
python app.py
```

Open in browser:

```
http://127.0.0.1:5000
```

---

## 🌍 Real-World Use Case

A customer receives a lengthy car lease agreement from a dealer and is unsure about hidden charges or risks.
By uploading the contract to this system, the customer can quickly understand key terms, identify risks, and ask questions through a chatbot before making a decision.

---

## 🚫 Scope Clarification

* ✔ Focuses on contract understanding and negotiation
* ❌ Does not predict car prices
* ❌ Does not calculate vehicle depreciation
* ❌ Does not replace legal professionals

---

## 🔮 Future Enhancements

* Support for additional contract types
* Improved user interface
* Multi-contract comparison
* Advanced risk scoring

---

## 👤 Author

**Rohith V**
B.Tech – Computer Science (AI & ML)

```
