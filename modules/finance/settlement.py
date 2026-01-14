import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional

# Mocking imports from your existing structure
# In production, these would import actual SQLAlchemy models
from .models import Invoice, LineItem, Client
from .journal import JournalEngine

class SettlementEngine:
    """
    The Judge.
    Translates operational physics (Logistics/Industrial events) into 
    commercial certainty (Invoices).
    """

    VAT_RATE = Decimal('0.15')

    def __init__(self, db_session):
        self.db = db_session
        self.journal = JournalEngine(db_session)

    def capitalize_event(self, event_type: str, payload: Dict) -> Dict:
        """
        The Entry Point. Receives a raw event dictionary from the modules.
        
        :param event_type: 'LOGISTICS_DELIVERY' or 'INDUSTRIAL_BATCH'
        :param payload: Dict containing 'client_id', 'qty', 'rate', 'ref'
        """
        print(f"[{datetime.datetime.now()}] CORTEX :: ANALYZING EVENT :: {event_type}")

        # 1. GOVERNANCE: Check Credit Limit
        client_id = payload.get('client_id')
        estimated_total = Decimal(payload.get('qty')) * Decimal(payload.get('rate'))
        
        if not self._check_credit_governance(client_id, estimated_total):
            return {
                "status": "BLOCKED", 
                "reason": "Credit Limit Exceeded. Manual Override Required."
            }

        # 2. CONSTRUCTION: Build the Invoice Object
        invoice = self._construct_invoice(payload)

        # 3. EXECUTION: Commit to Ledger
        # The 'settlement' is only real when it hits the journal.
        journal_entry = self.journal.post_entry(
            description=f"Auto-Settlement: {event_type}",
            debit_account="Accounts Receivable",
            credit_account="Sales Revenue", 
            amount=invoice['total_excl_vat'],
            tax_amount=invoice['vat_amount']
        )

        return {
            "status": "SETTLED",
            "invoice_number": invoice['invoice_number'],
            "journal_ref": journal_entry['id'],
            "total_due": str(invoice['total_due'])
        }

    def _check_credit_governance(self, client_id: str, new_debt: Decimal) -> bool:
        """
        Simulates the 'Cortex Analysis' from your dashboard.
        Returns False if the new debt pushes client over limit.
        """
        # In a real scenario, query Client model here
        # Mocking logic for 'Orion Energy'
        current_debt = Decimal('850000.00') 
        credit_limit = Decimal('1000000.00')
        
        utilization = (current_debt + new_debt) / credit_limit
        
        if utilization > 1.0:
            print(f"!! GOVERNANCE ALERT !! Client {client_id} exceeds limit.")
            return False
            
        print(f"GOVERNANCE PASS :: Utilization at {utilization*100:.1f}%")
        return True

    def _construct_invoice(self, data: Dict) -> Dict:
        """
        Internal factory to build the invoice structure with precise rounding.
        """
        qty = Decimal(str(data['qty']))
        rate = Decimal(str(data['rate']))
        
        subtotal = (qty * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        vat = (subtotal * self.VAT_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total = subtotal + vat

        # This dictionary mimics the structure you'd save to your DB
        return {
            "invoice_number": f"INV-{datetime.datetime.now().year}-{data.get('ref', '000')}",
            "client_id": data['client_id'],
            "date_issued": datetime.datetime.now(),
            "lines": [
                {"description": data.get('desc'), "qty": qty, "rate": rate, "total": subtotal}
            ],
            "total_excl_vat": subtotal,
            "vat_amount": vat,
            "total_due": total
        }

# --- TEST HARNESS (Run this file directly to test) ---
if __name__ == "__main__":
    # Mock Database Session
    mock_db = {} 
    
    # Initialize Engine
    engine = SettlementEngine(mock_db)
    
    # SIMULATION: Industrial Sensor Trigger
    test_payload = {
        "client_id": "ORION_ENERGY",
        "qty": 4500,        # Liters
        "rate": 22.50,      # Rands per Liter
        "ref": "SENSOR_901",
        "desc": "Heavy Fuel Oil (HFO) - Grade A"
    }

    # Run
    result = engine.capitalize_event("INDUSTRIAL_BATCH", test_payload)
    print("\n--- RESULT ---")
    print(result)
