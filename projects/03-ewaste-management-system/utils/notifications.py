"""
Notification service for email and SMS
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from config import config
from utils.logger import email_logger
from abc import ABC, abstractmethod

# ==================== EMAIL SERVICE ====================

class EmailProvider(ABC):
    """Base email provider"""
    
    @abstractmethod
    def send_email(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        pass

class GmailProvider(EmailProvider):
    """Gmail email provider"""
    
    def send_email(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = config.GMAIL_EMAIL
            msg["To"] = to
            
            if html:
                msg.attach(MIMEText(body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))
            
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(config.GMAIL_EMAIL, config.GMAIL_PASSWORD)
                server.sendmail(config.GMAIL_EMAIL, to, msg.as_string())
            
            email_logger.info(f"Email sent successfully to {to}")
            return True
        except Exception as e:
            email_logger.error(f"Failed to send email to {to}: {str(e)}")
            return False

class SendGridProvider(EmailProvider):
    """SendGrid email provider"""
    
    def send_email(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail, Email, To, Content
            
            sg = sendgrid.SendGridAPIClient(config.SENDGRID_API_KEY)
            
            mail = Mail(
                from_email=Email("noreply@ewaste.com"),
                to_emails=To(to),
                subject=subject,
                plain_text_content=body if not html else None,
                html_content=body if html else None
            )
            
            response = sg.send(mail)
            email_logger.info(f"Email sent successfully to {to} via SendGrid")
            return response.status_code in [200, 201, 202]
        except Exception as e:
            email_logger.error(f"Failed to send email via SendGrid: {str(e)}")
            return False

class EmailService:
    """Email service wrapper"""
    
    def __init__(self):
        if config.EMAIL_PROVIDER == "gmail":
            self.provider = GmailProvider()
        elif config.EMAIL_PROVIDER == "sendgrid":
            self.provider = SendGridProvider()
        else:
            self.provider = None
            email_logger.warning("No email provider configured")
    
    def send_submission_confirmation(self, to: str, submission_id: str, name: str) -> bool:
        """Send submission confirmation email"""
        subject = f"E-Waste Submission Confirmation - {submission_id}"
        body = f"""
        Dear {name},
        
        Thank you for submitting your e-waste!
        
        Your Request ID: {submission_id}
        Status: Pending
        
        Our team will contact you soon to arrange collection.
        
        Best regards,
        E-Waste Management Team
        """
        return self.provider.send_email(to, subject, body) if self.provider else False
    
    def send_collection_scheduled(self, to: str, name: str, date: str, time: str) -> bool:
        """Send collection scheduled notification"""
        subject = "Your E-Waste Collection is Scheduled"
        body = f"""
        Dear {name},
        
        Your e-waste collection has been scheduled!
        
        Scheduled Date: {date}
        Time Window: {time}
        
        Please ensure someone is available at the scheduled time.
        
        Best regards,
        E-Waste Management Team
        """
        return self.provider.send_email(to, subject, body) if self.provider else False
    
    def send_collection_completed(self, to: str, name: str, co2_saved: float) -> bool:
        """Send collection completed notification"""
        subject = "Your E-Waste Collection is Complete!"
        body = f"""
        Dear {name},
        
        Your e-waste has been successfully collected and recycled!
        
        Environmental Impact:
        - CO₂ Saved: {co2_saved} kg
        - Thank you for helping protect our environment!
        
        Best regards,
        E-Waste Management Team
        """
        return self.provider.send_email(to, subject, body) if self.provider else False
    
    def send_incentive_notification(self, to: str, name: str, reward_amount: float) -> bool:
        """Send incentive/reward notification"""
        subject = f"You've Earned ₹{reward_amount}!"
        body = f"""
        Dear {name},
        
        Congratulations! You've earned ₹{reward_amount} for your e-waste contribution.
        
        This amount can be:
        1. Transferred to your bank account
        2. Used as store credit
        3. Donated to environmental causes
        
        Visit your dashboard to claim your reward!
        
        Best regards,
        E-Waste Management Team
        """
        return self.provider.send_email(to, subject, body) if self.provider else False

# ==================== SMS SERVICE ====================

class SMSService:
    """SMS notification service using Twilio"""
    
    def send_sms(self, phone: str, message: str) -> bool:
        """Send SMS message"""
        try:
            from twilio.rest import Client
            
            if not config.TWILIO_ACCOUNT_SID or not config.TWILIO_AUTH_TOKEN:
                email_logger.warning("Twilio credentials not configured")
                return False
            
            client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
            
            message_obj = client.messages.create(
                body=message,
                from_=config.TWILIO_PHONE_NUMBER,
                to=phone
            )
            
            email_logger.info(f"SMS sent successfully to {phone}")
            return True
        except Exception as e:
            email_logger.error(f"Failed to send SMS: {str(e)}")
            return False
    
    def send_collection_reminder(self, phone: str, name: str) -> bool:
        """Send collection reminder SMS"""
        message = f"Hi {name}, your e-waste collection is scheduled tomorrow. Please ensure availability. - E-Waste Team"
        return self.send_sms(phone, message)
    
    def send_status_update(self, phone: str, submission_id: str, status: str) -> bool:
        """Send status update SMS"""
        message = f"Your e-waste request {submission_id} status: {status}. Thanks for recycling! - E-Waste Team"
        return self.send_sms(phone, message)

# ==================== NOTIFICATION GATEWAY ====================

class NotificationService:
    """Unified notification service"""
    
    def __init__(self):
        self.email = EmailService()
        self.sms = SMSService()
    
    def notify_submission_received(self, email: str, phone: str, name: str, submission_id: str) -> bool:
        """Notify user that submission was received"""
        self.email.send_submission_confirmation(email, submission_id, name)
        self.sms.send_sms(phone, f"We received your e-waste request {submission_id}. You'll be contacted soon.")
        return True
    
    def notify_collection_scheduled(self, email: str, phone: str, name: str, date: str, time: str) -> bool:
        """Notify user about scheduled collection"""
        self.email.send_collection_scheduled(email, name, date, time)
        self.sms.send_collection_reminder(phone, name)
        return True
    
    def notify_collection_completed(self, email: str, phone: str, name: str, co2_saved: float, reward: float) -> bool:
        """Notify user about completed collection"""
        self.email.send_collection_completed(email, name, co2_saved)
        self.email.send_incentive_notification(email, name, reward)
        self.sms.send_status_update(phone, "collection_complete", "Completed & Recycled")
        return True

# Global instance
notification_service = NotificationService()
