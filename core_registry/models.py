from sqlalchemy import Column, String, Boolean, Float, Integer, Enum as SqlEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
import enum
from datetime import datetime

Base = declarative_base()

# --- Regal Standard Enums ---
class LeadStatus(str, enum.Enum):
    SUSPECT = "suspect"
    TARGET = "target"
    PROSPECT = "prospect"
    QUALIFIED = "qualified"

class Sector(str, enum.Enum):
    AGRICULTURE = "Agriculture"
    MINING = "Mining"
    LOGISTICS = "Logistics"
    RETAIL = "Retail"
    PROPERTY = "Property"

class Region(str, enum.Enum):
    GAUTENG = "Gauteng"
    WESTERN_CAPE = "Western Cape"
    KZN = "KwaZulu-Natal"
    EASTERN_CAPE = "Eastern Cape"

# --- The Suspect Entity (Expanded) ---
class SuspectEntity(Base):
    __tablename__ = 'vm_core_registry'

    # A. Identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    registration_number = Column(String, unique=True, nullable=False, index=True)
    legal_name = Column(String, nullable=False)
    trading_name = Column(String) # The Brand
    
    # Segmentation
    industry_sector = Column(SqlEnum(Sector), index=True) 
    operational_region = Column(SqlEnum(Region), index=True)
    
    # B. Commercial Potential (The Prize)
    annual_revenue = Column(Float) # ZAR
    est_energy_spend = Column(Float) # Monthly ZAR proxy
    site_ownership = Column(Boolean, default=False) # True = Owns Land (PPA), False = Lease

    # C. Intelligence Flags
    deterioration_risk = Column(Boolean, default=False) # The Kill Switch
    status = Column(SqlEnum(LeadStatus), default=LeadStatus.SUSPECT)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Suspect {self.legal_name} | Risk: {self.deterioration_risk}>"
