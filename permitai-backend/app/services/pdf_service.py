from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime
from app.models.application import Application

class PDFService:
    @staticmethod
    def generate_permit_certificate(application: Application, permit_number: str) -> bytes:
        """
        Generate official permit certificate as PDF in memory
        
        Returns:
            bytes: PDF document binary data
        """
        # Create PDF in memory
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
            title="Building Permit Certificate"
        )
        
        # Container for PDF elements
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#1a4d7a'),  # Government blue
            spaceAfter=20,
            alignment=1,  # Center
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1a4d7a'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        normal_style = styles['Normal']
        
        # Spacer
        elements.append(Spacer(1, 0.2*inch))
        
        # Title
        elements.append(Paragraph(
            "OFFICIAL BUILDING PERMIT CERTIFICATE",
            title_style
        ))
        
        # Government seal / header
        elements.append(Paragraph(
            "Bruhat Bangalore Mahanagara Palike (BBMP)<br/>Building Department",
            ParagraphStyle(
                'Subheader',
                parent=normal_style,
                fontSize=11,
                alignment=1,
                textColor=colors.HexColor('#333333')
            )
        ))
        
        elements.append(Spacer(1, 0.25*inch))
        
        # ============================================================================
        # PERMIT DETAILS SECTION
        # ============================================================================
        elements.append(Paragraph("Permit Details", heading_style))
        
        permit_details_data = [
            ['Permit Number:', permit_number],
            ['Application ID:', application.application_id],
            ['Issue Date:', datetime.utcnow().strftime("%d-%m-%Y")],
            ['Validity:', '1 Year from issue date'],
            ['Status:', 'APPROVED'],
        ]
        
        permit_table = Table(
            permit_details_data,
            colWidths=[2.2*inch, 4.0*inch],
            style=TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ])
        )
        elements.append(permit_table)
        elements.append(Spacer(1, 0.15*inch))
        
        # ============================================================================
        # APPLICANT INFORMATION
        # ============================================================================
        elements.append(Paragraph("Applicant Information", heading_style))
        
        applicant_data = [
            ['Name:', application.applicant_name or 'N/A'],
            ['Email:', application.applicant_email or 'N/A'],
            ['Phone:', application.applicant_phone or 'N/A'],
            ['Address:', f"{application.applicant_address_line1 or ''} {application.applicant_address_line2 or ''}".strip() or 'N/A'],
            ['City/State:', f"{application.applicant_address_city or ''}, {application.applicant_address_state or ''} {application.applicant_address_zip or ''}".strip() or 'N/A'],
        ]
        
        applicant_table = Table(
            applicant_data,
            colWidths=[2.2*inch, 4.0*inch],
            style=TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ])
        )
        elements.append(applicant_table)
        elements.append(Spacer(1, 0.15*inch))
        
        # ============================================================================
        # PROPERTY INFORMATION
        # ============================================================================
        elements.append(Paragraph("Property Information", heading_style))
        
        property_data = [
            ['Property Address:', f"{application.property_address_line1 or ''} {application.property_address_line2 or ''}".strip() or 'N/A'],
            ['Property Size:', f"{application.property_size or 'N/A'} {application.property_size_unit or 'sq ft'}"],
            ['Current / Proposed Use:', f"{application.property_current_use or 'N/A'} / {application.property_proposed_use or 'N/A'}"],
            ['Zone/Ward:', application.property_ward_number or 'N/A'],
        ]
        
        property_table = Table(
            property_data,
            colWidths=[2.2*inch, 4.0*inch],
            style=TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ])
        )
        elements.append(property_table)
        elements.append(Spacer(1, 0.15*inch))
        
        # ============================================================================
        # PROJECT INFORMATION
        # ============================================================================
        elements.append(Paragraph("Project Information", heading_style))
        
        cost_val = f"₹{application.estimated_cost:,.2f}" if application.estimated_cost else 'N/A'
        project_data = [
            ['Permit Type:', application.permit_type or 'N/A'],
            ['Project Description:', application.project_description or 'N/A'],
            ['Estimated Cost:', cost_val],
            ['Construction Area:', f"{application.construction_area or 'N/A'} {application.construction_area_unit or 'sq ft'}"],
        ]
        
        project_table = Table(
            project_data,
            colWidths=[2.2*inch, 4.0*inch],
            style=TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ])
        )
        elements.append(project_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # ============================================================================
        # TERMS & CONDITIONS
        # ============================================================================
        elements.append(Paragraph("Terms & Conditions", heading_style))
        
        terms = """
        1. This permit is valid for <b>ONE YEAR</b> from the date of issue.<br/>
        2. The permit holder must comply with all building codes and regulations.<br/>
        3. Work must commence within 6 months of permit issuance.<br/>
        4. Periodic inspections will be conducted during construction.<br/>
        5. Any structural changes require prior written approval.<br/>
        6. Final inspection required before occupancy certificate issuance.
        """
        
        elements.append(Paragraph(terms, ParagraphStyle(
            'Terms',
            parent=normal_style,
            fontSize=8,
            leading=11,
            textColor=colors.HexColor('#555555')
        )))
        elements.append(Spacer(1, 0.25*inch))
        
        # ============================================================================
        # SIGNATURE SECTION
        # ============================================================================
        signature_data = [
            ['Officer in Charge', '', 'Permit Holder'],
            ['_________________', '', '_________________'],
            [f"Date: {datetime.utcnow().strftime('%d-%m-%Y')}", '', ''],
        ]
        
        signature_table = Table(
            signature_data,
            colWidths=[2.5*inch, 1.2*inch, 2.5*inch],
            style=TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ])
        )
        elements.append(signature_table)
        elements.append(Spacer(1, 0.15*inch))
        
        # ============================================================================
        # FOOTER
        # ============================================================================
        footer_text = f"""
        This is a digitally generated document. For authenticity, verify permit number {permit_number} 
        on the BBMP website. Generated on {datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')}.
        """
        
        elements.append(Paragraph(footer_text, ParagraphStyle(
            'Footer',
            parent=normal_style,
            fontSize=7,
            alignment=1,
            textColor=colors.HexColor('#999999')
        )))
        
        # ============================================================================
        # BUILD PDF
        # ============================================================================
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
