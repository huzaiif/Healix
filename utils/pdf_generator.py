import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

def generate_clinical_pdf(report_data: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    warning_style = ParagraphStyle(
        'Warning',
        parent=styles['Normal'],
        textColor=colors.red,
        fontSize=11,
        spaceAfter=10
    )
    
    elements = []
    
    # Header Logo / App Name
    elements.append(Paragraph("<b>AI Health Assistant</b>", title_style))
    elements.append(Paragraph("Clinical-Grade Health Assessment Report", styles['Heading3']))
    elements.append(Spacer(1, 12))
    
    # Patient Info Table
    patient_info = report_data.get('patient_info', {})
    patient_data = [
        ["Patient Name", patient_info.get('name', 'N/A'), "Date", datetime.now().strftime("%Y-%m-%d %H:%M")],
        ["Age", str(patient_info.get('age', 'N/A')), "Gender", patient_info.get('gender', 'N/A')],
        ["Report ID", str(report_data.get('report_id', 'N/A'))[:8], "Patient ID", str(patient_info.get('patient_id', 'N/A'))]
    ]
    t_patient = Table(patient_data, colWidths=[80, 150, 80, 150])
    t_patient.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 1, colors.lightgrey),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('FONTNAME', (3,0), (3,-1), 'Helvetica'),
    ]))
    elements.append(t_patient)
    elements.append(Spacer(1, 20))
    
    # Vitals Table
    elements.append(Paragraph("Vitals Recorded", heading_style))
    vitals = report_data.get('vitals', {})
    vitals_data = [
        ["Heart Rate", f"{vitals.get('heart_rate', 'N/A')} bpm", "Temperature", f"{vitals.get('temperature', 'N/A')} °F"],
        ["SpO2", f"{vitals.get('spo2', 'N/A')} %", "Blood Pressure", f"{vitals.get('sys_bp', 'N/A')} / {vitals.get('dia_bp', 'N/A')} mmHg"]
    ]
    t_vitals = Table(vitals_data, colWidths=[100, 130, 100, 130])
    t_vitals.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#f0f4f8")),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor("#f0f4f8")),
        ('GRID', (0,0), (-1,-1), 1, colors.lightgrey),
        ('ALIGN', (1,0), (1,-1), 'CENTER'),
        ('ALIGN', (3,0), (3,-1), 'CENTER'),
    ]))
    elements.append(t_vitals)
    elements.append(Spacer(1, 20))
    
    # AI Assessment
    elements.append(Paragraph("AI Assessment & Summary", heading_style))
    analysis = report_data.get('ai_analysis', {})
    summary_text = analysis.get('summary', 'No summary provided.')
    elements.append(Paragraph(summary_text, normal_style))
    elements.append(Spacer(1, 10))
    
    risk_level = analysis.get('risk_level', 'Unknown')
    risk_color = colors.red if risk_level.lower() == 'high' else (colors.orange if risk_level.lower() == 'moderate' else colors.green)
    risk_para = Paragraph(f"<b>Assessed Risk Level:</b> <font color='{risk_color.hexval()}'>{risk_level.upper()}</font>", normal_style)
    elements.append(risk_para)
    elements.append(Spacer(1, 10))
    
    conditions = analysis.get('probable_conditions', [])
    if conditions:
        elements.append(Paragraph("<b>Probable Conditions (Non-Diagnostic):</b>", normal_style))
        for cond in conditions:
            elements.append(Paragraph(f"• {cond}", normal_style))
        elements.append(Spacer(1, 10))
        
    # Recommendations
    elements.append(Paragraph("Recommendations", heading_style))
    recs = report_data.get('recommendations', {})
    for k, v in recs.items():
        if isinstance(v, list) and v:
            elements.append(Paragraph(f"<b>{k.replace('_', ' ').title()}</b>", normal_style))
            for item in v:
                 elements.append(Paragraph(f"• {item}", normal_style))
                 
    elements.append(Spacer(1, 20))
    
    # Emergency Warnings
    flags = report_data.get('emergency_flags', {})
    if flags.get('critical_symptoms_to_watch', []) or flags.get('seek_immediate_care_if'):
        elements.append(Paragraph("EMERGENCY WARNINGS", heading_style))
        for sym in flags.get('critical_symptoms_to_watch', []):
             elements.append(Paragraph(f"• Watch for: {sym}", warning_style))
        if flags.get('seek_immediate_care_if'):
             elements.append(Paragraph(f"<b>Seek immediate care if:</b> {flags.get('seek_immediate_care_if')}", warning_style))
             
    elements.append(Spacer(1, 30))
    
    # Disclaimer
    disclaimer_text = "DISCLAIMER: This report is generated by an AI Health Assistant and is strictly for informational purposes. It is NOT a medical diagnosis, and the AI is not a licensed medical professional. Always consult a doctor or healthcare provider for medical advice, diagnosis, or treatment."
    elements.append(Paragraph(disclaimer_text, ParagraphStyle('Disclaimer', parent=styles['Italic'], fontSize=9, textColor=colors.gray)))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_simple_pdf(title: str, content: str) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    normal_style = styles['Normal']
    
    elements = []
    
    # Header Log / App Name
    elements.append(Paragraph("<b>AI Health Assistant</b>", title_style))
    elements.append(Paragraph(title, styles['Heading3']))
    elements.append(Spacer(1, 12))
    
    # Content
    for line in content.split('\n'):
        # Convert markdown bold to reportlab bold
        line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
        if line.strip():
            elements.append(Paragraph(line, normal_style))
            elements.append(Spacer(1, 6))
            
    # Disclaimer
    elements.append(Spacer(1, 30))
    disclaimer_text = "DISCLAIMER: This report is generated by an AI Health Assistant and is strictly for informational purposes. It is NOT a medical diagnosis, and the AI is not a licensed medical professional."
    elements.append(Paragraph(disclaimer_text, ParagraphStyle('Disclaimer', parent=styles['Italic'], fontSize=9, textColor=colors.gray)))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
