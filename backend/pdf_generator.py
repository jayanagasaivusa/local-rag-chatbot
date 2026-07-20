import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_pdf_report(title: str, content: str, source: str) -> io.BytesIO:
    buffer = io.BytesIO()
    
    # 1. Page Setup - 0.75-inch margins (54 points)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    story = []
    
    # 2. Corporate Style Sheets
    styles = getSampleStyleSheet()
    
    # Custom Brand Colors
    PRIMARY_COLOR = HexColor("#1E3A8A")   # Deep Corporate Blue
    TEXT_COLOR = HexColor("#1F2937")      # Slate Gray Body text
    MUTED_COLOR = HexColor("#6B7280")     # Light gray for footer/source
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=PRIMARY_COLOR,
        spaceAfter=15,
        alignment=TA_LEFT
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=MUTED_COLOR,
        spaceAfter=25,
        alignment=TA_LEFT
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        textColor=TEXT_COLOR,
        spaceAfter=12
    )
    
    footer_style = ParagraphStyle(
        'DocFooter',
        parent=styles['Italic'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        textColor=MUTED_COLOR,
        spaceBefore=30
    )

    # 3. Building the Document Flow (The Story)
    
    # Header Accent Bar (Optional, but looks premium)
    story.append(Paragraph("BUSINESS INTELLIGENCE REPORT", subtitle_style))
    
    # Report Title
    story.append(Paragraph(f"Analysis: {title}", title_style))
    story.append(Spacer(1, 10))
    
    # Clean Paragraph Formatting for Body Content
    # We replace manual newlines with proper paragraph spaces so it wraps beautifully across pages
    paragraphs = content.split('\n')
    for p in paragraphs:
        clean_p = p.strip()
        if clean_p:
            story.append(Paragraph(clean_p, body_style))
    
    story.append(Spacer(1, 20))
    
    # Source / Citation Footer
    story.append(Paragraph(f"Data Verified From: {source}", footer_style))
    
    # 4. Generate PDF
    doc.build(story)
    
    buffer.seek(0)
    return buffer