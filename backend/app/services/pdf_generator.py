from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import HexColor
from io import BytesIO
from datetime import datetime
import re


def markdown_to_pdf(report_markdown: str, property_address: str = None) -> BytesIO:
    """
    Convert the markdown analysis report to a professional PDF.
    Returns a BytesIO buffer containing the PDF.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#2c3e50'),
        spaceAfter=10,
        spaceBefore=14,
        fontName='Helvetica-Bold'
    )
    
    subheader_style = ParagraphStyle(
        'CustomSubHeader',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        leading=16,
        textColor=HexColor('#333333'),
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['BodyText'],
        fontSize=11,
        leading=16,
        textColor=HexColor('#333333'),
        leftIndent=20,
        spaceAfter=6
    )
    
    verdict_red_style = ParagraphStyle(
        'VerdictRed',
        parent=body_style,
        textColor=HexColor('#c0392b'),
        fontName='Helvetica-Bold',
        fontSize=12
    )
    
    verdict_amber_style = ParagraphStyle(
        'VerdictAmber',
        parent=body_style,
        textColor=HexColor('#e67e22'),
        fontName='Helvetica-Bold',
        fontSize=12
    )
    
    verdict_green_style = ParagraphStyle(
        'VerdictGreen',
        parent=body_style,
        textColor=HexColor('#27ae60'),
        fontName='Helvetica-Bold',
        fontSize=12
    )
    
    # Build story
    story = []
    
    # Title
    story.append(Paragraph("PKH Legal Brain", title_style))
    story.append(Paragraph("Auction Legal Pack Analysis", header_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Property address if available
    if property_address:
        story.append(Paragraph(f"<b>Property:</b> {property_address}", body_style))
        story.append(Spacer(1, 0.1*inch))
    
    # Date
    analysis_date = datetime.now().strftime("%d %B %Y at %H:%M")
    story.append(Paragraph(f"<b>Analysis Date:</b> {analysis_date}", body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Parse and convert markdown content
    lines = report_markdown.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # Detect verdict with color coding
        if line.upper().startswith('**VERDICT:'):
            verdict_text = line.replace('**VERDICT:', '').replace('**', '').strip()
            if 'RED' in verdict_text.upper():
                story.append(Paragraph(f"<b>VERDICT:</b> {verdict_text}", verdict_red_style))
            elif 'AMBER' in verdict_text.upper():
                story.append(Paragraph(f"<b>VERDICT:</b> {verdict_text}", verdict_amber_style))
            elif 'GREEN' in verdict_text.upper():
                story.append(Paragraph(f"<b>VERDICT:</b> {verdict_text}", verdict_green_style))
            else:
                story.append(Paragraph(f"<b>VERDICT:</b> {verdict_text}", body_style))
            story.append(Spacer(1, 0.15*inch))
        
        # H2 headers (##)
        elif line.startswith('## '):
            header_text = line.replace('## ', '').replace('**', '')
            story.append(Paragraph(header_text, header_style))
        
        # H3 headers (###) or **Header**
        elif line.startswith('### ') or (line.startswith('**') and line.endswith('**') and len(line) < 50):
            header_text = line.replace('### ', '').replace('**', '')
            story.append(Paragraph(header_text, subheader_style))
        
        # Numbered lists (1. 2. 3.)
        elif re.match(r'^\d+\.\s', line):
            # Clean and format
            text = escape_xml(line)
            story.append(Paragraph(text, bullet_style))
        
        # Bullet points (- or *)
        elif line.startswith('- ') or line.startswith('* '):
            text = escape_xml(line[2:])
            story.append(Paragraph(f"• {text}", bullet_style))
        
        # Regular paragraphs
        else:
            text = escape_xml(line)
            # Make bold text work
            text = text.replace('**', '<b>', 1).replace('**', '</b>', 1)
            story.append(Paragraph(text, body_style))
        
        i += 1
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def escape_xml(text: str) -> str:
    """Escape special XML characters for ReportLab."""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    # Handle bold markdown
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    return text
