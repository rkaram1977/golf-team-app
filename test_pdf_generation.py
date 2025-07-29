# test_pdf_generation.py
import os
import sys
from datetime import datetime

# Add project root to path to allow imports from src
project_root = "/home/ubuntu/golf_team_app"
sys.path.insert(0, project_root)

from fpdf import FPDF

# --- Define necessary utility functions locally --- 
def sanitize_text(text):
    """Simplified sanitize function for testing footer text."""
    if text is None:
        return ""
    text = str(text)
    # Basic replacement for copyright symbol
    text = text.replace("©", "(c)")
    # Keep only basic ASCII characters for simplicity in test
    return ''.join(c if 32 <= ord(c) < 127 else '' for c in text)

def get_category(handicap):
    """Simplified get_category function (not used in footer test)."""
    if handicap <= 10: return 'A'
    elif handicap <= 18: return 'B'
    elif handicap <= 27: return 'C'
    else: return 'D'
# --- End local utility functions ---

try:
    # Paths
    static_folder = os.path.join(project_root, "src", "static")
    scramble_logo_path = os.path.join(static_folder, "logo.jpeg")
    karam_logo_path = os.path.join(static_folder, "logo-karam.jpeg")
    dejavu_sans_path = os.path.join(static_folder, "fonts", "DejaVuSans.ttf")
    output_pdf_path = "/home/ubuntu/test_footer.pdf"

    # Check paths
    if not os.path.exists(scramble_logo_path): raise FileNotFoundError("Scramble logo not found")
    if not os.path.exists(karam_logo_path): raise FileNotFoundError("Karam logo not found")
    if not os.path.exists(dejavu_sans_path): raise FileNotFoundError("DejaVuSans font not found")

    # Create PDF
    class PDF(FPDF):
        def header(self): pass
        def footer(self): pass

    pdf = PDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("DejaVuSans", "", dejavu_sans_path, uni=True)
    pdf.add_font("DejaVuSans", "B", dejavu_sans_path, uni=True)
    pdf.add_font("DejaVuSans", "I", dejavu_sans_path, uni=True)
    pdf.add_page()
    pdf.set_font("DejaVuSans", size=11)

    # --- Content (Simplified for footer test) ---
    pdf.image(scramble_logo_path, x=pdf.w/2 - 40, y=10, w=80)
    pdf.ln(30) # Add some space
    pdf.cell(0, 10, "Sample Content Line 1", 0, 1)
    pdf.cell(0, 10, "Sample Content Line 2", 0, 1)
    # Add enough content to potentially push footer down
    for i in range(25): # Increased lines to ensure footer is near bottom
         pdf.cell(0, 6, f"More content line {i+1}", 0, 1)

    # --- Footer Logic (Copied & Adjusted from team_routes.py) ---
    logo_height_estimate = 10 # Estimativa da altura do logo após redimensionar para w=30
    text_height = 6 # Altura da linha de texto
    bottom_margin = 15

    # Posição Y para o texto "Design by:"
    design_by_y = pdf.h - bottom_margin - logo_height_estimate - text_height - 5 # 5mm acima do logo
    pdf.set_y(design_by_y)
    pdf.set_font("helvetica", "", 10) # Use helvetica as in original code
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, text_height, sanitize_text("Design by:"), 0, 1, "C")

    # Posição Y para o logo
    logo_y = design_by_y + text_height
    pdf.image(karam_logo_path, x=pdf.w/2 - 15, y=logo_y, w=30) # w=30

    # Posição Y para o texto de direitos autorais
    copyright_y = logo_y + logo_height_estimate + 2 # 2mm abaixo do logo
    pdf.set_y(copyright_y)
    pdf.cell(0, text_height, sanitize_text("© 2025 Todos os direitos reservados a Karam Design"), 0, 1, "C")
    # --- End Footer Logic ---

    # Save PDF
    pdf.output(output_pdf_path)
    print(f"PDF gerado com sucesso em: {output_pdf_path}")

except Exception as e:
    print(f"Erro ao gerar PDF de teste: {e}")
    sys.exit(1)

