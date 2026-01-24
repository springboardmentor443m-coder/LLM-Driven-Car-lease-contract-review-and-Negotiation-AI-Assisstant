Environment Variables
env
# API Keys
OPENAI_API_KEY=sk-...
# Database
DATABASE_URL=sqlite:///contracts.db
# or for PostgreSQL:
# DATABASE_URL=postgresql://user:pass@localhost/car_lease

# Server
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000

# OCR
TESSERACT_PATH=/usr/bin/tesseract


Run the Application

bash
# Terminal 1: Start Backend
cd backend
python app.py

# Terminal 2: Start Frontend
cd frontend
streamlit run app.py
