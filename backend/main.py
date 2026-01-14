
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# 1. IMPORT THE NEW VIN ROUTER HERE
from routers import ocr, llm, vin 
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Car Lease Negotiator")

# Allow React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, change this to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. REGISTER THE VIN ROUTER HERE
app.include_router(ocr.router, prefix="/ocr", tags=["OCR"])
app.include_router(llm.router, prefix="/llm", tags=["LLM"])
app.include_router(vin.router, prefix="/vin", tags=["VIN"])

@app.get("/health")
def health_check():
    return {"status": "active", "system": "Car Lease Assistant"}

if __name__ == "__main__":
    # Run the application directly
    # You can also run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
