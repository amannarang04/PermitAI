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
    def _build_html_email(
        greeting_name: str,
        status_text: str,
        message_body: str,
        details: dict,
        cta_text: str = None,
        cta_url: str = None,
        status_type: str = "info"  # info, success, warning, danger
    ) -> str:
        """
        Builds a modern, professional, and responsive HTML email template using inline CSS.
        """
        color_map = {
            "success": {
                "bg": "#E8F5E9",
                "text": "#2E7D32",
                "border": "#A5D6A7"
            },
            "warning": {
                "bg": "#FFF3E0",
                "text": "#E65100",
                "border": "#FFCC80"
            },
            "danger": {
                "bg": "#FFEBEE",
                "text": "#C62828",
                "border": "#FFCDD2"
            },
            "info": {
                "bg": "#E3F2FD",
                "text": "#1565C0",
                "border": "#90CAF9"
            }
        }
        colors = color_map.get(status_type, color_map["info"])
        
        details_html = ""
        if details:
            details_html += """
            <div style="background-color: #F8F9FA; border: 1px solid #E9ECEF; border-radius: 8px; padding: 16px; margin: 20px 0;">
                <table style="width: 100%; border-collapse: collapse; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 14px;">
            """
            for label, value in details.items():
                details_html += f"""
                    <tr>
                        <td style="padding: 6px 0; color: #6C757D; font-weight: 500; width: 40%; vertical-align: top;">{label}</td>
                        <td style="padding: 6px 0; color: #212529; font-weight: 600; vertical-align: top;">{value}</td>
                    </tr>
                """
            details_html += """
                </table>
            </div>
            """
            
        cta_html = ""
        if cta_text and cta_url:
            cta_html = f"""
            <div style="text-align: center; margin: 30px 0;">
                <a href="{cta_url}" style="background-color: #0A2540; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: bold; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 15px; display: inline-block; box-shadow: 0 4px 6px rgba(10, 37, 64, 0.15); transition: background-color 0.2s ease;">
                    {cta_text}
                </a>
            </div>
            """
            
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{status_text}</title>
        </head>
        <body style="margin: 0; padding: 0; background-color: #F4F6F9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; -webkit-font-smoothing: antialiased;">
            <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; margin-top: 40px; margin-bottom: 40px; box-shadow: 0 8px 16px rgba(0,0,0,0.05); border: 1px solid #E9ECEF;">
                <!-- Header -->
                <tr>
                    <td style="background-color: #0A2540; padding: 24px; text-align: center; border-bottom: 4px solid #F3A83B;">
                        <span style="color: #ffffff; font-size: 22px; font-weight: 800; letter-spacing: 1px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                            Permit<span style="color: #F3A83B;">AI</span>
                        </span>
                        <div style="color: #A5B4FC; font-size: 11px; margin-top: 4px; font-weight: 500; letter-spacing: 0.5px;">BRUHAT BENGALURU MAHANAGARA PALIKE</div>
                    </td>
                </tr>
                
                <!-- Status Banner -->
                <tr>
                    <td style="padding: 20px 30px 0 30px;">
                        <div style="background-color: {colors['bg']}; color: {colors['text']}; border: 1px solid {colors['border']}; border-radius: 8px; padding: 12px 16px; font-size: 14px; font-weight: 600; text-align: center; letter-spacing: 0.5px;">
                            {status_text.upper()}
                        </div>
                    </td>
                </tr>
                
                <!-- Content -->
                <tr>
                    <td style="padding: 30px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 15px; line-height: 1.6; color: #495057;">
                        <h4 style="margin-top: 0; color: #212529; font-size: 17px; font-weight: 600;">Dear {greeting_name},</h4>
                        <p style="margin-bottom: 20px;">{message_body}</p>
                        
                        {details_html}
                        
                        {cta_html}
                        
                        <p style="margin-top: 25px; margin-bottom: 5px; color: #6C757D; font-size: 14px;">Best regards,</p>
                        <p style="margin-top: 0; font-weight: 600; color: #0A2540; font-size: 14px;">PermitAI Team (BBMP)</p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        return html_template

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
            msg = f"We have successfully received your building permit application for {app.permit_type}. Our automated systems are currently validating the details. You can track your application status anytime on the PermitAI citizen portal."
            details = {
                "Application ID": app.application_id,
                "Permit Type": app.permit_type,
                "City": "Bangalore (BBMP)",
                "Submitted At": app.submitted_at.strftime("%Y-%m-%d %H:%M:%S") if app.submitted_at else "N/A"
            }
            html = NotificationService._build_html_email(
                greeting_name=to_name,
                status_text="Application Received",
                message_body=msg,
                details=details,
                cta_text="Track Application",
                cta_url=f"http://localhost:3000/track/{app.application_id}",
                status_type="info"
            )
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
            msg = "Congratulations! Your permit application has been APPROVED. Your official building permit certificate is now available for download. You can download the digital copy from your dashboard or pick up the physical copy from the department municipal office."
            details = {
                "Application ID": app.application_id,
                "Permit Number": permit_number,
                "Permit Type": app.permit_type,
                "Approval Date": app.decided_at.strftime("%Y-%m-%d") if app.decided_at else "N/A"
            }
            html = NotificationService._build_html_email(
                greeting_name=to_name,
                status_text="Permit Approved",
                message_body=msg,
                details=details,
                cta_text="Download Permit PDF",
                cta_url=f"http://localhost:8000/api/applications/{app.application_id}/download-permit",
                status_type="success"
            )
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
            msg = "We regret to inform you that your permit application has been REJECTED. Please review the reasons and required changes below. You may log into the portal to review specific officer comments, upload corrected documents, and resubmit."
            details = {
                "Application ID": app.application_id,
                "Permit Type": app.permit_type,
                "Rejection Reason": rejection_reason,
                "Decision Date": app.decided_at.strftime("%Y-%m-%d") if app.decided_at else "N/A"
            }
            html = NotificationService._build_html_email(
                greeting_name=to_name,
                status_text="Application Rejected",
                message_body=msg,
                details=details,
                cta_text="Review & Resubmit",
                cta_url=f"http://localhost:3000/resubmit/{app.application_id}",
                status_type="danger"
            )
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
            msg = "Your building permit application is currently on hold due to missing required documentation. Please log in and upload the missing documents listed below. Once the files are uploaded, verification will resume."
            details = {
                "Application ID": app.application_id,
                "Permit Type": app.permit_type,
                "Missing Documents": ", ".join([doc.replace('_', ' ').title() for doc in missing_docs])
            }
            html = NotificationService._build_html_email(
                greeting_name=to_name,
                status_text="Action Required: Missing Documents",
                message_body=msg,
                details=details,
                cta_text="Upload Documents",
                cta_url=f"http://localhost:3000/resubmit/{app.application_id}",
                status_type="warning"
            )
            return NotificationService.send_email(to_email, subject, html)
        return True

