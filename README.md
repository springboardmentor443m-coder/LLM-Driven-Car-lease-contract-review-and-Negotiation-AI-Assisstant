\# 🚗 LLM-Driven Car Lease Contract Review \& Negotiation AI Assistant



An AI-powered system that analyzes car lease/loan contracts, extracts SLA terms, evaluates fairness \& risk, integrates vehicle intelligence, and assists users with negotiation through an AI chatbot.



---



\## 🎯 Project Objectives



\- Analyze car lease / loan contracts automatically

\- Extract important SLA clauses using AI

\- Evaluate contract fairness and risks

\- Integrate real vehicle intelligence via VIN

\- Provide AI-powered negotiation assistance

\- Generate contract review reports (PDF)

\- Offer a clean interactive dashboard



---



\## 🧠 System Architecture



Frontend (HTML + JS Dashboard)

↓

FastAPI Backend (REST APIs)

↓

OCR / PDF Parsing

↓

SLA Extraction (Regex + LLM)

↓

Fairness Scoring Engine

↓

Vehicle Intelligence APIs

↓

AI Chatbot (Groq LLM)







---



\## ⚙️ Tech Stack



\### Backend

\- \*\*FastAPI\*\*

\- \*\*SQLAlchemy\*\*

\- \*\*MySQL\*\*

\- \*\*Uvicorn\*\*

\- \*\*Jinja2\*\*

\- \*\*ReportLab (PDF Generation)\*\*



\### AI / NLP

\- \*\*Groq LLM (LLaMA-3)\*\*

\- Regex + Rule-based logic

\- Prompt-engineered chatbot



\### Frontend

\- HTML5

\- CSS (Glassmorphism UI)

\- JavaScript (Fetch API)



---



\## 📦 Features by Phase



\### ✅ Phase 3 – Contract Upload \& OCR

\- Upload PDF / Image contracts

\- Extract raw contract text



\### ✅ Phase 4 – SLA Extraction

\- APR

\- Lease term

\- Monthly payment

\- Mileage limits

\- Penalties \& termination clauses



\### ✅ Phase 5 – Vehicle Intelligence

\- VIN detection

\- Make / Model / Year

\- Vehicle metadata from APIs



\### ✅ Phase 6 – Fairness Scoring \& Risk Analysis

\- Fairness score (0–100)

\- Risk level: Low / Medium / High

\- Risk explanation factors



\### ✅ Phase 7 – AI Negotiation Assistant

\- Context-aware chatbot

\- Risk explanation

\- Negotiation suggestions

\- Contract Q\&A



\### ✅ Phase 7A–7C

\- Unified contract risk report

\- Downloadable PDF report

\- Interactive dashboard UI



---



\## 🚀 How to Run the Project



\### 1️⃣ Clone Repository

```bash

git clone <repo-url>

cd car-contract-ai





2️⃣ Create Virtual Environment

python -m venv venv

venv\\Scripts\\activate



3️⃣ Install Dependencies

pip install -r requirements.txt



4️⃣ Set Environment Variables

setx GROQ\_API\_KEY "your\_groq\_api\_key"



5️⃣ Run Backend

uvicorn backend.main:app --reload



6️⃣ Open Dashboard

http://127.0.0.1:8000



🧪 API Documentation



Swagger UI:

👉 http://127.0.0.1:8000/docs



📄 Sample Outputs



Fairness Score \& Risk Summary



Vehicle Intelligence Report



AI Chatbot Responses



PDF Contract Review Report



👨‍💻 Author



Shanmuk Venkat Kakarapalli

Intern – AI / Data Engineering



🏆 Mentorship \& Learning Outcomes



Hands-on FastAPI development



AI-driven contract analysis



Prompt engineering



REST API design



Full-stack integration



Real-world internship project experience





---



\## ✅ Step 3: Add README to Git



Now run these commands:



```bash

git add README.md

git commit -m "Added project README documentation"

git push origin shanmuk-venkat



🎉 Result



After push:



README appears on GitHub repo homepage



Mentor can instantly understand:



What you built



How it works



Your contribution quality



This README is internship-grade + recruiter-friendly 🔥

