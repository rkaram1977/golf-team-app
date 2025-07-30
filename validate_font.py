import sys
try:
    # Ensure fpdf2 is importable
    from fpdf import FPDF
    # Define the path to the font file relative to the execution directory
    font_path = "src/static/fonts/DejaVuSans.ttf"
    pdf = FPDF()
    # Attempt to add the font
    pdf.add_font("DejaVu", "", font_path, uni=True)
    print("Fonte DejaVuSans.ttf carregada com sucesso pelo fpdf2.")
except ImportError as ie:
    print(f"Erro de importação: {ie}. Verifique se fpdf2 está instalado.")
except Exception as e:
    # Catch specific FPDF exceptions if possible, otherwise general exception
    print(f"Erro ao carregar a fonte DejaVuSans.ttf: {e}")

