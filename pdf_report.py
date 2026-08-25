from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
import os
from datetime import datetime
import json

# Stel fonts in voor cyaan/navy cyberpunk stijl
try:
    # Probeer fonts te registreren (als ze beschikbaar zijn)
    pdfmetrics.registerFont(TTFont('JetBrainsMono', 'JetBrainsMono-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('JetBrainsMono-Bold', 'JetBrainsMono-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('Orbitron', 'Orbitron-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('Orbitron-Bold', 'Orbitron-Bold.ttf'))
except:
    # Fallback naar standaard fonts
    pass

# Kleuren: near-black navy, cyaan, violet
COLOR_NAVY = colors.HexColor('#0A0E1A')
COLOR_CYAN = colors.HexColor('#00D4FF')
COLOR_VIOLET = colors.HexColor('#7C3AED')
COLOR_DARK_CYAN = colors.HexColor('#0088AA')
COLOR_WHITE = colors.HexColor('#F0F4FF')
COLOR_GRAY = colors.HexColor('#8899BB')
COLOR_RED = colors.HexColor('#FF3355')
COLOR_GREEN = colors.HexColor('#00FF88')
COLOR_YELLOW = colors.HexColor('#FFB800')

def create_pdf_report(session_data, filename='nis2_report.pdf'):
    """Maak een NIS2 audit rapport in de cyberpunk stijl"""
    
    # Parse data
    questions = session_data.get('questions', [])
    answers = session_data.get('answers', [])
    scores = session_data.get('scores', {})
    scan_results = session_data.get('scan_results', {})
    advice = session_data.get('advice', [])
    domain = scan_results.get('domain', 'Onbekend domein')
    
    # Maak het document
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        title=f"NIS2 Audit Rapport - {domain}",
        author="NIS2 Audit Tool",
        subject="Cybersecurity Assessment"
    )
    
    # Stijlen
    styles = getSampleStyleSheet()
    
    # Hoofdstijl voor titels
    title_style = ParagraphStyle(
        'CyberTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=COLOR_CYAN,
        alignment=TA_CENTER,
        spaceAfter=20,
        leading=30
    )
    
    # Subtitel stijl
    subtitle_style = ParagraphStyle(
        'CyberSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14,
        textColor=COLOR_GRAY,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    # Kopstijl (voor headers)
    heading_style = ParagraphStyle(
        'CyberHeading',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=COLOR_CYAN,
        spaceAfter=12,
        spaceBefore=20,
        leading=22
    )
    
    # Normale tekststijl
    normal_style = ParagraphStyle(
        'CyberNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        textColor=COLOR_WHITE,
        leading=16,
        spaceAfter=8
    )
    
    # Actie stijl (voor advies)
    action_style = ParagraphStyle(
        'CyberAction',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=COLOR_WHITE,
        leading=14,
        spaceAfter=6,
        leftIndent=10
    )
    
    # Sectiekop stijl
    section_style = ParagraphStyle(
        'CyberSection',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=COLOR_VIOLET,
        spaceAfter=10,
        spaceBefore=15,
        leading=18
    )
    
    # Build de content
    story = []
    
    # === PAGINA 1: COVER ===
    # Grote logo/cyberpunk cover
    story.append(Paragraph("NIS2", title_style))
    story.append(Paragraph("Cybersecurity Audit", title_style))
    story.append(Spacer(1, 10*mm))
    story.append(Paragraph(f"<font color='{COLOR_VIOLET.hexval()}'>⚡ {domain} ⚡</font>", subtitle_style))
    story.append(Spacer(1, 5*mm))
    
    # Datum
    now = datetime.now().strftime("%d-%m-%Y %H:%M")
    story.append(Paragraph(f"<font color='{COLOR_GRAY.hexval()}'>Rapport gegenereerd: {now}</font>", subtitle_style))
    story.append(Spacer(1, 5*mm))
    
    # Score meter
    percentage = scores.get('percentage', 0)
    score_color = COLOR_GREEN if percentage >= 70 else COLOR_YELLOW if percentage >= 40 else COLOR_RED
    
    story.append(Spacer(1, 10*mm))
    story.append(Paragraph(f"<font color='{score_color.hexval()}' size='48'><b>{percentage}%</b></font>", 
                          ParagraphStyle('Score', parent=styles['Normal'], alignment=TA_CENTER)))
    story.append(Paragraph("Algehele NIS2-compliantie score", 
                          ParagraphStyle('ScoreLabel', parent=styles['Normal'], textColor=COLOR_GRAY, alignment=TA_CENTER)))
    
    story.append(Spacer(1, 10*mm))
    
    # Disclaimer
    story.append(Paragraph("<font color='#556688' size='8'>Dit rapport is een indicatieve beoordeling en geen vervanging voor formeel juridisch advies.<br/>De NIS2-richtlijn is complex en de implementatie kan per sector verschillen.</font>",
                          ParagraphStyle('Disclaimer', parent=styles['Normal'], alignment=TA_CENTER, textColor=COLOR_GRAY)))
    
    story.append(PageBreak())
    
    # === PAGINA 2: SAMENVATTING ===
    story.append(Paragraph("Samenvatting", heading_style))
    story.append(Spacer(1, 5*mm))
    
    # Samenvattingstekst
    if percentage >= 70:
        summary = "Je cybersecurity is op orde! Je scoort goed op de meeste NIS2-criteria. Blijf investeren in onderhoud en bewustwording om dit niveau te behouden."
    elif percentage >= 40:
        summary = "Je hebt een basis op orde, maar er zijn belangrijke verbeterpunten. Focus op de categorieën met de laagste scores en werk stap voor stap aan verbetering."
    else:
        summary = "Er is significante actie nodig om aan de NIS2-vereisten te voldoen. Begin met een risico-inventarisatie en pak de meest kritieke gaten aan."
    
    story.append(Paragraph(summary, normal_style))
    story.append(Spacer(1, 5*mm))
    
    # Scores per categorie in een tabel
    story.append(Paragraph("Scores per categorie", section_style))
    
    # Tabel data
    table_data = [['Categorie', 'Score', 'Status']]
    for category, data in scores.get('categories', {}).items():
        pct = data['percentage']
        status = '✅' if pct >= 70 else '⚠️' if pct >= 40 else '❌'
        table_data.append([category, f"{pct}%", status])
    
    # Tabel stijl
    t = Table(table_data, colWidths=[100*mm, 40*mm, 30*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), COLOR_CYAN),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#1A2035')),
        ('TEXTCOLOR', (0, 1), (-1, -1), COLOR_WHITE),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#2A3050')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t)
    story.append(Spacer(1, 5*mm))
    
    story.append(PageBreak())
    
    # === PAGINA 3: TECHNISCHE SCAN ===
    story.append(Paragraph("Technische Scan Resultaten", heading_style))
    story.append(Spacer(1, 5*mm))
    
    if scan_results and scan_results.get('success'):
        # DNS info
        dns = scan_results.get('results', {}).get('dns', {})
        if dns.get('ip'):
            story.append(Paragraph(f"<b>Domein:</b> {domain} ({dns.get('ip')})", normal_style))
        
        # Poort scan
        ports = scan_results.get('results', {}).get('ports', {})
        if ports:
            story.append(Paragraph("Poort scan resultaten:", section_style))
            open_ports = [p for p, data in ports.items() if data.get('open')]
            if open_ports:
                port_str = ", ".join([f"{p} ({ports[p]['service']})" for p in open_ports])
                story.append(Paragraph(f"<font color='{COLOR_GREEN.hexval()}'>Open poorten: {port_str}</font>", normal_style))
            else:
                story.append(Paragraph("<font color='#8899BB'>Geen open poorten gevonden in de scan.</font>", normal_style))
        
        # SSL info
        ssl = scan_results.get('results', {}).get('ssl', {})
        if ssl.get('success'):
            story.append(Paragraph("SSL/TLS certificaat:", section_style))
            cert = ssl.get('cert', {})
            if cert.get('subject'):
                subject = dict(cert['subject'][0]) if isinstance(cert['subject'], list) else {}
                story.append(Paragraph(f"<b>Onderwerp:</b> {subject.get('commonName', 'Onbekend')}", normal_style))
            if cert.get('notAfter'):
                story.append(Paragraph(f"<b>Geldig tot:</b> {cert.get('notAfter')}", normal_style))
        
        # HTTP headers
        headers = scan_results.get('results', {}).get('headers', {})
        if headers.get('success'):
            story.append(Paragraph("Webserver informatie:", section_style))
            story.append(Paragraph(f"<b>Server:</b> {headers.get('server', 'Onbekend')}", normal_style))
            story.append(Paragraph(f"<b>HTTP Status:</b> {headers.get('status', 'Onbekend')}", normal_style))
        
        # Mail servers
        mail = scan_results.get('results', {}).get('mail', {})
        if mail.get('mx_records'):
            story.append(Paragraph("Mail servers (MX records):", section_style))
            story.append(Paragraph(", ".join(mail.get('mx_records', [])), normal_style))
    else:
        story.append(Paragraph("Technische scan kon niet worden uitgevoerd voor dit domein.", normal_style))
        if scan_results.get('error'):
            story.append(Paragraph(f"<font color='{COLOR_RED.hexval()}'>Fout: {scan_results.get('error')}</font>", normal_style))
    
    story.append(Spacer(1, 5*mm))
    
    # === PAGINA 4: ADVIES EN ACTIES ===
    story.append(Paragraph("Wat kun je nu concreet doen?", heading_style))
    story.append(Spacer(1, 5*mm))
    
    if advice:
        for item in advice:
            # Bepaal kleur op basis van prioriteit
            priority = item.get('priority', 'geel')
            color = COLOR_GREEN if priority == 'groen' else COLOR_YELLOW if priority == 'geel' else COLOR_RED if priority == 'rood' else COLOR_CYAN
            
            # Bepaal emoji
            emoji = '✅' if priority == 'groen' else '⚠️' if priority == 'geel' else '🚨' if priority == 'rood' else '💡'
            
            # Titel in kleur
            title_text = f"<font color='{color.hexval()}'><b>{emoji} {item.get('title', '')}</b></font>"
            story.append(Paragraph(title_text, normal_style))
            
            # Actie in normale tekst
            action_text = item.get('action', '')
            # Splits op newline voor meerdere regels
            for line in action_text.split('\n'):
                if line.strip():
                    story.append(Paragraph(f"• {line.strip()}", action_style))
            story.append(Spacer(1, 3*mm))
    else:
        story.append(Paragraph("Geen specifiek advies beschikbaar voor deze sessie.", normal_style))
    
    story.append(Spacer(1, 5*mm))
    
    # Voeg audit details toe
    story.append(Paragraph("Audit details", section_style))
    story.append(Paragraph(f"<b>Audit ID:</b> {session_data.get('session_id', 'N/A')}", normal_style))
    story.append(Paragraph(f"<b>Vragen beantwoord:</b> {len(answers)} van de 40", normal_style))
    story.append(Paragraph(f"<b>Totale score:</b> {scores.get('total_score', 0)} / {scores.get('max_score', 0)}", normal_style))
    
    # Build het document
    doc.build(story)
    return filename

def generate_report_data(session_id, db):
    """Haal alle data voor een rapport op"""
    # Hier zou je de data uit de database halen
    # Voor nu, retouneer dummy data
    return {
        'session_id': session_id,
        'questions': [],
        'answers': [],
        'scores': {},
        'scan_results': {},
        'advice': []
  }
