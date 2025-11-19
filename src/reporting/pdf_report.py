import logging
from datetime import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

logger = logging.getLogger("OSINT_Tool")


def generate_pdf_report(results: Dict[str, Any], output_file: str):
    """
    Generate a professional PDF report.
    
    Args:
        results: Results dictionary
        output_file: Output file path
    """
    logger.info(f"Generating PDF report: {output_file}")
    
    target = results.get('target', 'Unknown')
    target_type = results.get('target_type', 'Unknown')
    stats = results.get('statistics', {})
    
    # Create PDF
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title Page
    story.append(Paragraph("OSINT Intelligence Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"<b>Target:</b> {target}", styles['Normal']))
    story.append(Paragraph(f"<b>Type:</b> {target_type}", styles['Normal']))
    story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 0.5*inch))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    summary_data = [
        ['Metric', 'Value'],
        ['Total Results', str(stats.get('total_unique', 0))],
        ['High Quality Results', str(stats.get('high_quality_results', 0))],
        ['Average Quality Score', f"{stats.get('avg_quality_score', 0):.1f}/100"],
        ['Duplicates Removed', str(stats.get('duplicates_removed', 0))],
        ['Connections Found', str(stats.get('connections_found', 0))]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Email Enumeration
    if 'emails' in results and results['emails']:
        emails = results['emails']
        story.append(Paragraph("Email Enumeration", heading_style))
        story.append(Paragraph(f"Generated {emails.get('valid_format_count', 0)} potential email addresses", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        
        email_list = emails.get('emails_generated', [])[:20]
        if email_list:
            email_text = ", ".join(email_list)
            story.append(Paragraph(f"<font size=9>{email_text}</font>", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    # Social Media
    social_media = results.get('social_media', [])
    if social_media:
        story.append(Paragraph("Social Media Profiles", heading_style))
        
        social_data = [['Platform', 'Status', 'Quality Score']]
        for profile in social_media[:15]:
            social_data.append([
                profile.get('platform', 'N/A'),
                profile.get('status', 'N/A'),
                f"{profile.get('quality_score', 0)}/100"
            ])
        
        social_table = Table(social_data, colWidths=[2*inch, 2*inch, 1.5*inch])
        social_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(social_table)
        story.append(Spacer(1, 0.2*inch))
    
    # Search Results
    search_results = results.get('search_engines', [])
    if search_results:
        story.append(Paragraph("Search Engine Results", heading_style))
        
        search_data = [['Source', 'Title', 'Score']]
        for result in search_results[:15]:
            title = result.get('title', 'N/A')[:40]
            search_data.append([
                result.get('source', 'N/A'),
                title,
                f"{result.get('quality_score', 0)}/100"
            ])
        
        search_table = Table(search_data, colWidths=[1.5*inch, 3*inch, 1*inch])
        search_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(search_table)
    
    # Build PDF
    doc.build(story)
    
    logger.info(f"✓ PDF report saved to {output_file}")
