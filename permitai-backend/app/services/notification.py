import os
from typing import List
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sqlalchemy.orm import Session

from app.models.application import Application
from app.config import settings

class NotificationService:
    @staticmethod
    def get_sendgrid_client():
        # Check if key is mock or dummy
        if (settings.SENDGRID_API_KEY == "mock" or 
            settings.SENDGRID_API_KEY == "SG.xxxxxxxxxxxxx" or 
            not settings.SENDGRID_API_KEY or
            "xxx" in settings.SENDGRID_API_KEY):
            return None
        try:
            return SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        except Exception:
            return None

    @staticmethod
    def send_email(to_email: str, subject: str, html_content: str) -> bool:
        """
        Sends email using SendGrid or logs to stdout if SendGrid is unconfigured/mock.
        """
        client = NotificationService.get_sendgrid_client()
        if client:
            try:
                message = Mail(
                    from_email=(settings.FROM_EMAIL, settings.FROM_NAME),
                    to_emails=to_email,
                    subject=subject,
                    html_content=html_content
                )
                client.send(message)
                return True
            except Exception as e:
                # Log sendgrid failure and print to console
                print(f"[SendGrid Error] Failed to send email to {to_email}: {e}")
        
        # Local console email fallback
        print("\n" + "="*50)
        print("[MOCK EMAIL NOTIFICATION SYSTEM]")
        print(f"To: {to_email}")
        print(f"From: {settings.FROM_EMAIL} ({settings.FROM_NAME})")
        print(f"Subject: {subject}")
        print(f"Body:\n{html_content}")
        print("="*50 + "\n")
        return True

    @staticmethod
    def send_received_email(db: Session, app_id: int) -> bool:
        app = db.query(Application).filter(Application.id == app_id).first()
        if not app:
            return False
        
        to_email = app.applicant_email or app.citizen.email
        to_name = app.applicant_name or app.citizen.full_name or "Applicant"
        subject = f"Permit Application Received - {app.application_id}"
        html = f"""
        <html>
            <body>
                <h3>Dear {to_name},</h3>
                <p>We have successfully received your building permit application (ID: <strong>{app.application_id}</strong>) for <strong>{app.permit_type}</strong>.</p>
                <p>Our automated systems are currently validating the details. You can track your application status anytime on the PermitAI citizen portal.</p>
                <br/>
                <p>Best regards,</p>
                <p><strong>PermitAI Team</strong></p>
            </body>
        </html>
        """
        return NotificationService.send_email(to_email, subject, html)

    @staticmethod
    def send_approval_email(db: Session, app_id: int, permit_number: str) -> bool:
        app = db.query(Application).filter(Application.id == app_id).first()
        if not app:
            return False
        
        to_email = app.applicant_email or app.citizen.email
        to_name = app.applicant_name or app.citizen.full_name or "Applicant"
        subject = f"Permit APPROVED - {app.application_id}"
        html = f"""
        <html>
            <body>
                <h3>Dear {to_name},</h3>
                <p>Congratulations! Your permit application (ID: <strong>{app.application_id}</strong>) has been <strong>APPROVED</strong>.</p>
                <p>Your official building permit number is: <strong>{permit_number}</strong>.</p>
                <p>You can now download the digital copy of your permit from your dashboard or pick up the physical copy from the department municipal office.</p>
                <br/>
                <p>Best regards,</p>
                <p><strong>PermitAI Team</strong></p>
            </body>
        </html>
        """
        return NotificationService.send_email(to_email, subject, html)

    @staticmethod
    def send_rejection_email(db: Session, app_id: int, rejection_reason: str) -> bool:
        app = db.query(Application).filter(Application.id == app_id).first()
        if not app:
            return False
        
        to_email = app.applicant_email or app.citizen.email
        to_name = app.applicant_name or app.citizen.full_name or "Applicant"
        subject = f"Permit Application Update - REJECTED - {app.application_id}"
        html = f"""
        <html>
            <body>
                <h3>Dear {to_name},</h3>
                <p>We regret to inform you that your permit application (ID: <strong>{app.application_id}</strong>) has been <strong>REJECTED</strong>.</p>
                <p><strong>Reason for rejection:</strong><br/>{rejection_reason}</p>
                <p>You may log into the portal to review specific officer comments, upload corrected documents, and resubmit your application.</p>
                <br/>
                <p>Best regards,</p>
                <p><strong>PermitAI Team</strong></p>
            </body>
        </html>
        """
        return NotificationService.send_email(to_email, subject, html)

    @staticmethod
    def send_missing_documents_email(db: Session, app_id: int, missing_docs: List[str]) -> bool:
        app = db.query(Application).filter(Application.id == app_id).first()
        if not app:
            return False
        
        to_email = app.applicant_email or app.citizen.email
        to_name = app.applicant_name or app.citizen.full_name or "Applicant"
        subject = f"Action Required: Missing Documents for Permit {app.application_id}"
        docs_list = "".join([f"<li>{doc.replace('_', ' ').title()}</li>" for doc in missing_docs])
        html = f"""
        <html>
            <body>
                <h3>Dear {to_name},</h3>
                <p>Your building permit application (ID: <strong>{app.application_id}</strong>) is currently on hold due to missing required documentation.</p>
                <p>Please log in and upload the following documents:</p>
                <ul>
                    {docs_list}
                </ul>
                <p>Once the missing files are uploaded, automated verification will resume.</p>
                <br/>
                <p>Best regards,</p>
                <p><strong>PermitAI Team</strong></p>
            </body>
        </html>
        """
        return NotificationService.send_email(to_email, subject, html)
