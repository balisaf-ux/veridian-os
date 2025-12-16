from sqlalchemy.orm import Session
from core_registry.models import SuspectEntity

class IntelEngine:
    def __init__(self, db_session: Session):
        self.session = db_session

    def get_segment(self, sector=None, region=None, min_revenue=0):
        query = self.session.query(SuspectEntity)

        if sector and sector != "All":
            query = query.filter(SuspectEntity.industry_sector == sector)
        
        if region and region != "All":
            query = query.filter(SuspectEntity.operational_region == region)
            
        if min_revenue > 0:
            query = query.filter(SuspectEntity.annual_revenue >= min_revenue)

        return query.all()

    def run_deterioration_scan(self):
        # Finds entities where The Kill Switch is Active
        return self.session.query(SuspectEntity).filter(
            SuspectEntity.deterioration_risk == True
        ).all()

    def get_stats(self):
        total = self.session.query(SuspectEntity).count()
        risk_count = self.session.query(SuspectEntity).filter(
            SuspectEntity.deterioration_risk == True
        ).count()
        return total, risk_count
