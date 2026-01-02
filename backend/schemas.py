from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict


# ======================================================
# PHASE 4: SLA RESPONSE SCHEMA
# ======================================================
class SLAExtractionResponse(BaseModel):
    apr: float
    lease_term: int
    monthly_payment: float
    mileage_limit: int
    early_termination: str
    penalties: str
    fairness_score: int


# ======================================================
# PHASE 3 + PHASE 4: CONTRACT RESPONSE SCHEMA
# (NO VEHICLE DATA HERE — OPTION A)
# ======================================================
class ContractResponse(BaseModel):
    id: int
    file_name: str
    raw_text: str

    # None during Phase 3 (upload)
    # Filled during Phase 4 (SLA extraction)
    sla_extraction: Optional[SLAExtractionResponse] = None

    model_config = ConfigDict(from_attributes=True)


# ======================================================
# PHASE 5: VEHICLE INTELLIGENCE SCHEMAS
# (USED ONLY BY VEHICLE ENDPOINTS)
# ======================================================

class VehicleSpecsResponse(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    engine: Optional[str] = None
    transmission: Optional[str] = None


class VehicleInsightsResponse(BaseModel):
    # NHTSA + future sources (dynamic fields)
    nhtsa_data: Optional[Dict] = None
    data_sources: Optional[list[str]] = None


class VehicleInfoResponse(BaseModel):
    vin: str
    vehicle_specs: VehicleSpecsResponse
    vehicle_insights: VehicleInsightsResponse

# ======================================================
# PHASE 6: FAIRNESS RESPONSE
# ======================================================
class FairnessResponse(BaseModel):
    fairness_score: int
    risk_level: str
    risk_factors: list[str]
