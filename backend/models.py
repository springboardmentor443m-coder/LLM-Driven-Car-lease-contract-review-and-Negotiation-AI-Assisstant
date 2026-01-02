from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    Float,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .db import Base


# ======================================================
# CONTRACT MODEL (Phase 3+)
# ======================================================
class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)

    file_name = Column(String(255), nullable=False)
    raw_text = Column(Text, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ✅ ONE-TO-ONE relationship
    sla_extraction = relationship(
        "SLAExtraction",
        back_populates="contract",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,   # 🔥 important for CASCADE
    )


# ======================================================
# SLA EXTRACTION MODEL (Phase 4)
# ======================================================
class SLAExtraction(Base):
    __tablename__ = "sla_extractions"

    id = Column(Integer, primary_key=True, index=True)

    # ✅ Enforced 1-to-1 mapping
    contract_id = Column(
        Integer,
        ForeignKey("contracts.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # ✅ NUMERIC fields (critical fix)
    apr = Column(Float, nullable=True)
    lease_term = Column(Integer, nullable=True)
    monthly_payment = Column(Float, nullable=True)
    mileage_limit = Column(Integer, nullable=True)

    # ✅ TEXT fields
    early_termination = Column(Text, nullable=True)
    penalties = Column(Text, nullable=True)

    # ✅ SCORE
    fairness_score = Column(Integer, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    contract = relationship(
        "Contract",
        back_populates="sla_extraction",
    )
