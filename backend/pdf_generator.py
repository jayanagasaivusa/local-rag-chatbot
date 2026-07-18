from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

def generate_pdf_report(title: str, content: str, source: str) -> io.BytesIO:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Business Intelligence Report")
    
    # Title
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 100, f"Analysis: {title}")
    
    # Body
    c.setFont("Helvetica", 12)
    text_object = c.beginText(50, height - 130)
    text_object.textLines(content)
    c.drawText(text_object)
    
    # Footer (Source)
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 50, f"Generated from: {source}")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer