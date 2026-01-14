from datetime import datetime
from decimal import Decimal
from typing import Dict
from .models import JournalEntry

class JournalEngine:
    """
    The Historian.
    The immutable memory of the Magisterial System.
    Strictly enforces Double-Entry Bookkeeping (Debits = Credits).
    """

    def __init__(self, db_session):
        self.db = db_session

    def post_entry(self, description: str, debit_account: str, credit_account: str, amount: Decimal, tax_amount: Decimal = Decimal('0.00')) -> Dict:
        """
        Atomic Poster.
        Writes a balanced transaction to the permanent ledger.
        """
        
        # 1. GENERATE ID
        import uuid
        transaction_id = f"JRN-{str(uuid.uuid4())[:8].upper()}"
        total_credit = amount + tax_amount

        # 2. CONSTRUCT DATA PAYLOAD (JSON)
        # We pack the lines into a dictionary list for storage
        lines_data = [
            # A. The Debit Side (e.g., Accounts Receivable)
            {
                "account": debit_account,
                "debit": float(total_credit), 
                "credit": 0.0
            },
            # B. The Credit Side 1 (Revenue)
            {
                "account": credit_account,
                "debit": 0.0,
                "credit": float(amount)
            },
            # C. The Credit Side 2 (VAT Liability)
            {
                "account": "VAT Control Account",
                "debit": 0.0,
                "credit": float(tax_amount)
            }
        ]

        # 3. CREATE DB OBJECT
        new_entry = JournalEntry(
            id=transaction_id,
            timestamp=datetime.now(),
            description=description,
            lines_data=lines_data, # Storing as JSON
            status="POSTED"
        )

        # 4. COMMIT TO REALITY (The Missing Link)
        try:
            self.db.add(new_entry)
            self.db.commit()
            print(f"[{datetime.now()}] LEDGER :: WRITTEN TO DISK :: {description} | REF: {transaction_id}")
        except Exception as e:
            self.db.rollback()
            print(f"❌ LEDGER FAILURE: {e}")
            return {"status": "FAILED", "reason": str(e)}
        
        return {
            "id": transaction_id,
            "status": "COMMITTED",
            "journal_ref": transaction_id,
            "total_value": total_credit
        }

    def get_balance(self, account_name: str) -> Decimal:
        return Decimal('0.00') # Mock return for now
