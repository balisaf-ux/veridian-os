# VERIDIAN OPERATIONAL FINANCIAL SYSTEM
# CHART OF ACCOUNTS: SA LOGISTICS STANDARD (V1.0)

SA_LOGISTICS_COA = [
    {
        "code": "1200",
        "name": "Heavy Commercial Vehicles (Fleet)",
        "account_type": "ASSET",
        "tax_rule": "NO_VAT",
        "description": "Capital value of prime movers and rigid trucks."
    },
    {
        "code": "1210",
        "name": "Trailers & Equipment",
        "account_type": "ASSET",
        "tax_rule": "NO_VAT",
        "description": "Capital value of flatdecks, tautliners, and side-tippers."
    },
    {
        "code": "2200",
        "name": "Vehicle Asset Finance (Bank)",
        "account_type": "LIABILITY",
        "tax_rule": "NO_VAT",
        "description": "Long-term loans secured against the fleet."
    },
    {
        "code": "2500",
        "name": "VAT Control Account",
        "account_type": "LIABILITY",
        "tax_rule": "NO_VAT",
        "description": "System calculated VAT Output minus VAT Input (Owed to SARS)."
    },
    {
        "code": "4000",
        "name": "Transport Revenue (Local)",
        "account_type": "REVENUE",
        "tax_rule": "STANDARD_15",
        "description": "Logistics services rendered within RSA borders."
    },
    {
        "code": "4100",
        "name": "Transport Revenue (Cross-Border)",
        "account_type": "REVENUE",
        "tax_rule": "ZERO_RATED",
        "description": "Export logistics (e.g., JHB to Maputo/Gaborone)."
    },
    {
        "code": "5000",
        "name": "Fuel - Diesel",
        "account_type": "EXPENSE_DIRECT",
        "tax_rule": "STANDARD_15",
        "description": "Primary fuel costs. Critical for consumption analysis."
    },
    {
        "code": "5010",
        "name": "Lubricants, Oil & AdBlue",
        "account_type": "EXPENSE_DIRECT",
        "tax_rule": "STANDARD_15",
        "description": "Top-up fluids and additives."
    },
    {
        "code": "5100",
        "name": "Tyres & Retreads",
        "account_type": "EXPENSE_DIRECT",
        "tax_rule": "STANDARD_15",
        "description": "New tyre stock and casing retreading services."
    },
    {
        "code": "5200",
        "name": "Toll Fees & E-Tolls",
        "account_type": "EXPENSE_DIRECT",
        "tax_rule": "STANDARD_15",
        "description": "SANRAL and concession route fees."
    },
    {
        "code": "5300",
        "name": "Driver Wages (Trip-Based)",
        "account_type": "EXPENSE_DIRECT",
        "tax_rule": "NO_VAT",
        "description": "Variable wages linked to active trips."
    },
    {
        "code": "5400",
        "name": "Goods In Transit (GIT) Insurance",
        "account_type": "EXPENSE_DIRECT",
        "tax_rule": "NO_VAT",
        "description": "Load-specific insurance premiums."
    },
    {
        "code": "6000",
        "name": "Repairs & Maintenance (Parts)",
        "account_type": "EXPENSE_OVERHEAD",
        "tax_rule": "STANDARD_15",
        "description": "Scheduled servicing and breakdown parts."
    },
    {
        "code": "6500",
        "name": "Fines & Penalties",
        "account_type": "EXPENSE_OVERHEAD",
        "tax_rule": "NO_VAT",
        "description": "Traffic violations (Non-Deductible for Income Tax)."
    }
]
