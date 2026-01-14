from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class SovereignAsset(Base):
    """
    The Physical Wealth.
    Tracks what we own (Diesel in tanks, Coal at port).
    """
    __tablename__ = 'merc_assets'

    asset_id = Column(String(20), primary_key=True)   # e.g., TNK-DSL-01
    name = Column(String(100))                        # e.g., JHB Depot Tank A
    type = Column(String(50))                         # LIQUID (Fuel) or SOLID (Coal)
    capacity = Column(Numeric(12, 2))                 # Max Volume/Tonnage
    current_level = Column(Numeric(12, 2))            # Current On Hand
    avg_cost_price = Column(Numeric(12, 2))           # Weighted Avg Cost (ZAR)
    location = Column(String(100))                    # Geo-Location
    last_audit = Column(DateTime, default=datetime.now)

class TradePosition(Base):
    """
    The Financial Play.
    Tracks Arbitrage Deals (Buy ZAR -> Sell USD).
    """
    __tablename__ = 'merc_positions'

    deal_ref = Column(String(20), primary_key=True)   # e.g., EXP-2026-001
    commodity = Column(String(50))                    # Thermal Coal
    volume = Column(Numeric(12, 2))                   # Tonnage
    
    # The Arbitrage
    buy_currency = Column(String(10), default="ZAR")
    buy_rate = Column(Numeric(12, 2))                 # e.g., R 1450.00
    
    sell_currency = Column(String(10), default="USD")
    sell_rate = Column(Numeric(12, 2))                # e.g., $ 115.00
    
    fx_lock_rate = Column(Numeric(10, 4))             # ZAR/USD at lock
    status = Column(String(20))                       # OPEN, HEDGED, CLOSED
    created_at = Column(DateTime, default=datetime.now)

    from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class SovereignAsset(Base):
    """
    The Physical Wealth (Fuel/Coal).
    """
    __tablename__ = 'merc_assets'
    asset_id = Column(String(20), primary_key=True)
    name = Column(String(100))
    type = Column(String(50))
    capacity = Column(Numeric(12, 2))
    current_level = Column(Numeric(12, 2))
    avg_cost_price = Column(Numeric(12, 2))
    location = Column(String(100))
    last_audit = Column(DateTime, default=datetime.now)

class TradePosition(Base):
    """
    The Trade Deal (Arbitrage).
    """
    __tablename__ = 'merc_positions'
    deal_ref = Column(String(20), primary_key=True)
    commodity = Column(String(50))
    volume = Column(Numeric(12, 2))
    buy_currency = Column(String(10), default="ZAR")
    buy_rate = Column(Numeric(12, 2))
    sell_currency = Column(String(10), default="USD")
    sell_rate = Column(Numeric(12, 2))
    fx_lock_rate = Column(Numeric(10, 4))
    status = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)

class TreasuryInstrument(Base):
    """
    The Financial Power (LCs & Hedges).
    """
    __tablename__ = 'merc_treasury'
    
    instrument_id = Column(String(20), primary_key=True)  # e.g., LC-STD-001
    type = Column(String(20))                             # LC (Letter of Credit) or FWD (Forward Cover)
    institution = Column(String(50))                      # Standard Bank / Investec
    amount_face = Column(Numeric(12, 2))                  # Value in Currency
    currency = Column(String(10))                         # ZAR / USD
    expiry_date = Column(DateTime)
    status = Column(String(20))                           # ACTIVE, MATURED
    linked_deal_id = Column(String(20))                   # Links to a TradePosition
    created_at = Column(DateTime, default=datetime.now)
