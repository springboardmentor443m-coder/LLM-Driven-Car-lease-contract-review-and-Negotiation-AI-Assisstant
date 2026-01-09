🚗 LLM-Driven Car Lease Contract Review & Negotiation AI Assistant

An AI-powered system that analyzes car lease/loan contracts, extracts key SLA clauses, integrates vehicle intelligence, highlights contract pros & cons, and assists users with negotiation through an AI chatbot.

🎯 Project Objectives

Automatically analyze car lease / loan contracts

Extract important SLA clauses using AI

Provide transparent contract insights (Pros & Cons)

Integrate real vehicle intelligence via VIN

Assist users with negotiation using an AI chatbot

Generate downloadable contract review reports (PDF)

Offer a clean, interactive dashboard

🧠 System Architecture
Frontend (HTML + JS Dashboard)
        ↓
FastAPI Backend (REST APIs)
        ↓
OCR / PDF Parsing
        ↓
SLA Extraction (Regex + LLM)
        ↓
Contract Insight Engine (Pros & Cons)
        ↓
Vehicle Intelligence APIs (VIN-based)
        ↓
AI Negotiation Chatbot (Groq LLM)

⚙️ Tech Stack
Backend

FastAPI

SQLAlchemy

MySQL

Uvicorn

Jinja2

ReportLab (PDF generation)

AI / NLP

Groq LLM (LLaMA-3)

Regex + rule-based logic

Prompt-engineered chatbot

Frontend

HTML5

CSS (Glassmorphism UI)

JavaScript (Fetch API)

📦 Features by Phase
✅ Phase 3 – Contract Upload & OCR

Upload PDF / image contracts

Extract raw legal text safely

✅ Phase 4 – SLA Extraction

Extracted clauses include:

APR

Lease term

Monthly payment

Mileage limits

Penalties & early termination clauses

Designed with safe fallbacks to handle incomplete or noisy contracts.

✅ Phase 5 – Vehicle Intelligence

VIN detection from contract text

Vehicle make / model / year

Metadata via external vehicle APIs

🔁 Phase 6 – Contract Insights (Redesigned)

⚠️ Important Design Decision (Mentor-Driven)

Initially, a numeric fairness score was explored.
However, because vehicle price data is not reliably available, a numeric score could be misleading.

🔄 Redesign Outcome
The system now provides clear, explainable contract insights instead of arbitrary scoring.

✔ Contract Pros

Reasonable interest rate (if applicable)

Standard mileage allowance

No aggressive penalties detected

⚠ Contract Cons

Low mileage limits

Early termination charges

Ambiguous or strict penalty clauses

This approach is:

More transparent

Easier to justify in interviews

Aligned with real-world data constraints

✅ Phase 7 – AI Negotiation Assistant

Context-aware chatbot

Uses:

Contract text

Extracted SLA data

Vehicle intelligence

Example questions:

“Is this contract risky?”

“What can I negotiate?”

“Explain the mileage clause”

✅ Phase 7A–7C – Reporting & UI

Unified contract insight report (JSON)

Downloadable PDF contract review

Fully integrated dashboard UI

🚀 How to Run the Project
1️⃣ Clone Repository
git clone <repo-url>
cd car-contract-ai

2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Set Environment Variables
setx GROQ_API_KEY "your_groq_api_key"

5️⃣ Run Backend
uvicorn backend.main:app --reload

6️⃣ Open Dashboard

👉 http://127.0.0.1:8000

👉 API Docs: http://127.0.0.1:8000/docs

📄 Sample Outputs

SLA extraction summary

Vehicle intelligence report

Contract pros & cons insights

AI chatbot responses

PDF contract review report

👨‍💻 Author

Shanmuk Venkat Kakarapalli
Intern – AI / Data Engineering

🏆 Mentorship & Learning Outcomes

Hands-on FastAPI backend development

AI-driven contract analysis

Prompt engineering for real use cases

REST API design & documentation

Full-stack integration

Mentor-guided architectural redesign

Real-world internship project experience

📌 Git Workflow (Mentor Branch)
git add README.md
git commit -m "Updated README: contract insights redesign & chatbot focus"
git push origin shanmuk-venkat


🎉 Result

README appears clean on GitHub

Mentor sees clear reasoning + maturity

Project looks internship-grade & interview-ready