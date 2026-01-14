from fpdf import FPDF
from io import BytesIO

class SmartCompiler:
    @staticmethod
    def generate_pdf_quote(data):
        # Initialize PDF in A4 format
        pdf = FPDF()
        pdf.add_page()
        
        # --- 🎨 BRANDING COLORS ---
        MAGISTERIAL_BLUE = (46, 134, 193)  # Professional & Structured
        INDUSTRIAL_SLATE = (34, 34, 34)    # The Hard Economy Foundation
        TEXT_GREY = (80, 80, 80)

        # --- 💠 HEADER DESIGN ---
        # Blue Header Bar
        pdf.set_fill_color(*MAGISTERIAL_BLUE)
        pdf.rect(0, 0, 210, 40, 'F')
        
        # Logo Anchor 
        try:
            pdf.image('logo.png', 10, 10, 30)
        except:
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", 'B', 20)
            pdf.text(12, 25, "MAIS | OS")

        # Quote Title [cite: 2]
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 14)
        pdf.text(70, 20, "MAGISTERIAL SOVEREIGN QUOTATION")
        pdf.set_font("Arial", '', 10)
        pdf.text(70, 26, "SOVEREIGN ASSET ACQUISITION | REF: MAIS-TTE-2026-001")
        
        pdf.ln(35) # Move below header bar

        # --- 🤝 CLIENT & SYSTEM SUMMARY ---
        pdf.set_text_color(*INDUSTRIAL_SLATE)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, f"PREPARED FOR: {data['client']}", ln=True) # [cite: 3]
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 8, f"INFRASTRUCTURE: {data['system']}", ln=True) # [cite: 4]
        pdf.set_draw_color(*MAGISTERIAL_BLUE)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

        # --- 🚀 1. VALUE PROPOSITION ---
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(*MAGISTERIAL_BLUE)
        pdf.cell(0, 10, "1. THE VALUE PROPOSITION: SOVEREIGN TRANSFER", ln=True) # [cite: 5]
        
        pdf.set_text_color(*TEXT_GREY)
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 5, data['val_prop']) # 
        pdf.ln(5)

        # --- 🛠️ 2. CORE ASSET MODULES ---
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(*MAGISTERIAL_BLUE)
        pdf.cell(0, 10, "2. CORE ASSET MODULES", ln=True) # [cite: 8]
        
        features = [
            ("I. THE MARGIN SHIELD", "Fuel Forensics monitors tank levels to detect theft[cite: 9, 10]."),
            ("II. THE REVENUE HUNTER", "Mandla Protocol site timers and POD capture[cite: 11, 12]."),
            ("III. THE PHYSICS-LINK", "Hazchem and Tonnage compliance guardrails[cite: 13, 14]."),
            ("IV. THE TREASURY", "Double-Entry GL with Logistics COA[cite: 15, 16].")
        ]

        for f_title, f_desc in features:
            pdf.set_font("Arial", 'B', 10)
            pdf.set_text_color(*INDUSTRIAL_SLATE)
            pdf.cell(0, 7, f"  {f_title}", ln=True)
            pdf.set_font("Arial", '', 10)
            pdf.set_text_color(*TEXT_GREY)
            pdf.multi_cell(0, 5, f"    {f_desc}")
            pdf.ln(2)

        # --- 💰 3. COMMERCIAL TABLE ---
        pdf.ln(5)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 10)
        pdf.set_text_color(*INDUSTRIAL_SLATE)
        pdf.cell(110, 10, "  Item Description", 1, 0, 'L', True)
        pdf.cell(50, 10, "  Investment (ZAR)", 1, 1, 'L', True)
        
        pdf.set_font("Arial", '', 10)
        pdf.cell(110, 10, "  Sovereign Kernel Acquisition (v14.0 Core)", 1)
        pdf.cell(50, 10, "  R 165,000.00", 1, 1) # 
        pdf.cell(110, 10, "  TTE Custom Build (Forensics + Protocols)", 1)
        pdf.cell(50, 10, "  R 85,000.00", 1, 1) # 
        
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(*MAGISTERIAL_BLUE)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(110, 12, "  TOTAL ASSET INVESTMENT", 1, 0, 'L', True)
        pdf.cell(50, 12, "  R 250,000.00", 1, 1, 'L', True) # 

        # Wrap in BytesIO for Streamlit
        return BytesIO(pdf.output(dest='S'))
