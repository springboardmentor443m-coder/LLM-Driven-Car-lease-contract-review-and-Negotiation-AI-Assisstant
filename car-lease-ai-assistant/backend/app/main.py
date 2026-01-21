from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware


# ---- Import routes ----
from app.routes import upload
from app.routes import ocr
from app.routes import sla
from app.routes import vin
from app.routes import valuation
from app.routes import compare
from app.routes import negotiation

# ---- Create app ----
app = FastAPI(
    title="Car Lease AI Assistant",
    description="AI-powered lease contract analysis system",
    version="0.1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite React
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Health check ----
@app.get("/")
def health_check():
    return {"status": "Backend running"}

# ---- Register routers ----
app.include_router(upload.router, prefix="/api/contracts", tags=["Upload"])
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])
app.include_router(sla.router, prefix="/api/sla", tags=["SLA"])
app.include_router(vin.router, prefix="/api/vin", tags=["VIN"])
app.include_router(valuation.router, prefix="/api/valuation", tags=["Valuation"])

# ---- NEW MODULES ----
app.include_router(compare.router, prefix="/api/compare", tags=["Comparison"])
app.include_router(negotiation.router, prefix="/api/negotiate", tags=["Negotiation AI"])
