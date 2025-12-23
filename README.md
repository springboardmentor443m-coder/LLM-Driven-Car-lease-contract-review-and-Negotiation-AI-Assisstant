                              AI / LLM-Based Car Lease Contract Review and Chatbot Assistant

## Introduction

Car lease agreements are often lengthy and difficult for common users to understand. Important details such as interest rates, penalties, and mileage limits are usually hidden inside complex legal language. This project aims to simplify that process by building an AI-based system that can automatically analyze car lease contracts, extract key information, identify potential risks, and explain the contract in simple language.  

In addition to static analysis, the project also includes an interactive chatbot that allows users to ask questions about the analyzed contract and receive clear, context-aware answers.

---

## Project Objective

The main objective of this project is to help users understand car lease contracts before signing them. The system focuses on contract understanding and negotiation assistance rather than vehicle valuation or price prediction. By combining OCR, rule-based extraction, and large language models, the project provides both structured outputs and human-readable explanations.

---

## Overall Working of the System

The system begins by accepting a car lease contract in PDF format. The PDF may be text-based or scanned. Since OCR works on images, each page of the PDF is first converted into an image.

Tesseract OCR is then used to extract text from these images. The extracted text from all pages is combined and cleaned so that it can be processed further. From this text, important lease-related details such as monthly payment, interest rate (APR), down payment, mileage allowance, residual value, and early termination fees are identified using rule-based extraction logic.

Each extracted value is assigned a confidence score to indicate reliability. The system then checks the extracted information to identify potentially risky terms, such as high interest rates, high penalties, or low mileage limits. Based on these findings, negotiation suggestions are generated to help the user understand what aspects of the contract can be discussed with the dealer.

To make the output user-friendly, the extracted data is passed to an open-source Large Language Model (LLM) through the Groq API. The LLM generates a simple explanation of the contract, highlights risks, and summarizes negotiation advice in natural language.

---

## Chatbot Functionality

After the contract analysis is completed, users can interact with the system through a chatbot. The chatbot answers questions strictly based on the analyzed contract data and does not rely on external sources or assumptions.

The chatbot has been enhanced with intent-aware response handling. It understands whether a user is asking for a summary, risk explanation, negotiation advice, or clarification of a specific clause. This allows the chatbot to tailor its response style according to the user’s question.

Additionally, the chatbot maintains short-term conversation memory. It remembers recent questions and answers so that follow-up questions such as “Why is that risky?” can be answered correctly with proper context.

---

## Output of the System

The final output of the system consists of a structured JSON file containing extracted contract details, confidence scores, identified risks, and negotiation suggestions. Along with this, the chatbot provides interactive, plain-language explanations of the contract that are easy for non-technical users to understand.

---

## Technologies Used

The project is implemented using Python. Tesseract OCR is used for text extraction from scanned documents. PDF2Image and Pillow are used for PDF-to-image conversion and image handling. Flask is used to create a simple web-based chatbot interface. The Groq API is used to access an open-source LLM for explanation and chatbot responses. JSON is used to store structured outputs.

---

## Project Structure

├── contract_extractor.py      # OCR and contract information extraction
├── chatbot.py                 # Chatbot logic with intent detection and memory
├── run_chatbot.py             # Terminal-based chatbot interface
├── app.py                     # Web-based chatbot using Flask
├── test_pdf_to_img.py         # PDF to image conversion script
├── test_ocr.py                # OCR testing script
├── extracted_contract.json    # Extracted contract output
├── sample_datasets/           # Sample lease contract PDFs
├── templates/
│   └── index.html             # Chatbot web interface
├── README.md
├── .gitignore

---

## How to Run the Project

First, all required Python dependencies must be installed. Tesseract OCR should also be installed and properly added to the system PATH.

After installation, the contract extraction process can be executed to generate the structured output. Once the contract data is extracted, the chatbot can be run either through the terminal or via a simple web interface using Flask.

---

## Real-World Use Case

In a real-world scenario, a customer receives a car lease agreement from a dealer and is unsure about the terms. By uploading the contract to this system, the customer can quickly understand the key details, identify risks, and receive negotiation advice. The chatbot further allows the customer to ask specific questions about the contract without having to read the entire document.

---

## Scope Clarification

This project focuses on analyzing and explaining the contents of a car lease contract. It does not predict vehicle prices, calculate market depreciation, or replace legal professionals. The system is intended as an assistance tool to improve contract understanding and decision-making.

---

## Future Enhancements

Future improvements may include support for additional contract types, enhanced user interfaces, comparison between multiple contracts, and more advanced risk scoring mechanisms.

---

## Author

Rohith V  
B.Tech – Computer Science (AI & ML)
