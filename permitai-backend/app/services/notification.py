import os
import json
from typing import List
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.notification import InAppNotification
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
        
        # Append unsubscribe footer to the email
        unsubscribe_footer = """
        <br/><br/>
        <hr style="border: none; border-top: 1px solid #eeeeee;"/>
        <p style="font-size: 10px; color: #999999; text-align: center;">
            You are receiving this automated email regarding your PermitAI account. 
            To manage your notification settings or unsubscribe, please visit your account dashboard settings.
        </p>
        """
        full_content = html_content + unsubscribe_footer
        
        if client:
            try:
                message = Mail(
                    from_email=(settings.FROM_EMAIL, settings.FROM_NAME),
                    to_emails=to_email,
                    subject=subject,
                    html_content=full_content
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
        print(f"Body:\n{full_content}")
        print("="*50 + "\n")
        return True

    @staticmethod
    def create_in_app_notification(
        db: Session,
        user_id: int,
        title: str,
        message: str,
        application_id: str = None,
        notification_type: str = None
    ) -> InAppNotification:
        notification = InAppNotification(
            user_id=user_id,
            application_id=application_id,
            title=title,
            message=message,
            notification_type=notification_type
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def _get_user_preferences(user) -> dict:
        if not user or not hasattr(user, "notification_preferences") or user.notification_preferences is None:
            return {"email": True, "sms": True, "in_app": True}
        
        prefs = user.notification_preferences
        if isinstance(prefs, str):
            try:
                return json.loads(prefs)
            except Exception:
                return {"email": True, "sms": True, "in_app": True}
        return prefs

    @staticmethod
    def send_received_email(db: Session, app_id: int) -> bool:
        app = db.query(Application).filter(Application.id == app_id).first()
        if not app:
            return False
        
        user = app.citizen
        prefs = NotificationService._get_user_preferences(user)
        to_email = app.applicant_email or (user.email if user else None) or "applicant@example.com"
        to_name = app.applicant_name or (user.full_name if user else None) or "Applicant"
        subject = f"Permit Application Received - {app.application_id}"
        
        # In-App Notification
        if prefs.get("in_app", True) and user:
            NotificationService.create_in_app_notification(
                db=db,
                user_id=user.id,
                title=subject,
                message=f"We have successfully received your permit application for {app.permit_type}.",
                application_id=app.application_id,
                notification_type="received"
            )
            
        # SMS Notification
        if prefs.get("sms", True) and user and user.phone:
            print(f"[MOCK SMS] To: {user.phone} | Content: {subject} - Your permit application has been received and is being processed.")

        # Email Notification
        if prefs.get("email", True):
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
        return True

    @staticmethod
    def send_approval_email(db: Session, app_id: int, permit_number: str) -> bool:
        app = db.query(Application).filter(Application.id == app_id).first()
        if not app:
            return False
        
        user = app.citizen
        prefs = NotificationService._get_user_preferences(user)
        to_email = app.applicant_email or (user.email if user else None) or "applicant@example.com"
        to_name = app.applicant_name or (user.full_name if user else None) or "Applicant"
        subject = f"Permit APPROVED - {app.application_id}"

        # In-App Notification
        if prefs.get("in_app", True) and user:
            NotificationService.create_in_app_notification(
                db=db,
                user_id=user.id,
                title=subject,
                message=f"Congratulations! Your permit application for {app.permit_type} has been APPROVED. Permit Number: {permit_number}.",
                application_id=app.application_id,
                notification_type="approval"
            )
            
        # SMS Notification
        if prefs.get("sms", True) and user and user.phone:
            print(f"[MOCK SMS] To: {user.phone} | Content: {subject} - Approved! Permit Number: {permit_number}.")

        # Email Notification
        if prefs.get("email", True):
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
        return True

    @staticmethod
    def send_rejection_email(db: Session, app_id: int, rejection_reason: str) -> bool:
        app = db.query(Application).filter(Application.id == app_id).first()
        if not app:
            return False
        
        user = app.citizen
        prefs = NotificationService._get_user_preferences(user)
        to_email = app.applicant_email or (user.email if user else None) or "applicant@example.com"
        to_name = app.applicant_name or (user.full_name if user else None) or "Applicant"
        subject = f"Permit Application Update - REJECTED - {app.application_id}"

        # In-App Notification
        if prefs.get("in_app", True) and user:
            NotificationService.create_in_app_notification(
                db=db,
                user_id=user.id,
                title=subject,
                message=f"Your permit application for {app.permit_type} was rejected. Reason: {rejection_reason}.",
                application_id=app.application_id,
                notification_type="rejection"
            )
            
        # SMS Notification
        if prefs.get("sms", True) and user and user.phone:
            print(f"[MOCK SMS] To: {user.phone} | Content: {subject} - Rejected. Reason: {rejection_reason}.")

        # Email Notification
        if prefs.get("email", True):
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
        return True

    @staticmethod
    def send_missing_documents_email(db: Session, app_id: int, missing_docs: List[str]) -> bool:
        app = db.query(Application).filter(Application.id == app_id).first()
        if not app:
            return False
        
        user = app.citizen
        prefs = NotificationService._get_user_preferences(user)
        to_email = app.applicant_email or (user.email if user else None) or "applicant@example.com"
        to_name = app.applicant_name or (user.full_name if user else None) or "Applicant"
        subject = f"Action Required: Missing Documents for Permit {app.application_id}"
        docs_list = "".join([f"<li>{doc.replace('_', ' ').title()}</li>" for doc in missing_docs])

        # In-App Notification
        if prefs.get("in_app", True) and user:
            NotificationService.create_in_app_notification(
                db=db,
                user_id=user.id,
                title=subject,
                message=f"Action Required: Missing documents ({', '.join(missing_docs)}) for application {app.application_id}.",
                application_id=app.application_id,
                notification_type="missing_docs"
            )
            
        # SMS Notification
        if prefs.get("sms", True) and user and user.phone:
            print(f"[MOCK SMS] To: {user.phone} | Content: {subject} - Action Required: Please upload missing documents.")

        # Email Notification
        if prefs.get("email", True):
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
        return True
