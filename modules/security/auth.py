from datetime import datetime

def login_user(username, password):
    """
    Sovereign Authentication Engine with Temporal Guest Logic.
    """

    # 1. SOVEREIGN COMMAND (Permanent Access)
    if username == "Balisa" and password == "MAIS_SOVEREIGN":
        return {
            "username": "Balisa",
            "role": "Sovereign",
            "modules": ["UNIVERSAL"]  # Universal Access
        }

    # 2. EXTERNAL GUEST (Temporal Access - Logistics Only)
    expiry_date = datetime(2026, 1, 15, 16, 0)

    if username == "MAIS_GUEST_24H" and password == "LOGISTICS_PORTAL_2026":
        if datetime.now() < expiry_date:
            return {
                "username": "Guest_Procurement",
                "role": "External_Auditor",
                "modules": ["Logistics Cloud"]  # Restricted Access
            }
        return None  # Credential Expired

    # 3. INVALID CREDENTIALS
    return None
