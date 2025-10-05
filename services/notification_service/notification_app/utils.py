import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional
from django.conf import settings
from django.template import Template, Context
from django.core.mail import send_mail
from django.utils import timezone
from .models import Notification, NotificationTemplate, NotificationType, NotificationPreference

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'EMAIL_PORT', 587)
        self.smtp_username = getattr(settings, 'EMAIL_HOST_USER', '')
        self.smtp_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', self.smtp_username)
        self.use_tls = getattr(settings, 'EMAIL_USE_TLS', True)
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        message: str, 
        html_message: str = None,
        attachments: List[Dict] = None
    ) -> Dict:
        """
        Send email using Django's send_mail or SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            message: Plain text message
            html_message: HTML message (optional)
            attachments: List of attachments (optional)
        
        Returns:
            Dict with success status and message
        """
        try:
            # Debug logging
            logger.info(f"EmailService.send_email called with parameters:")
            logger.info(f"  to_email: '{to_email}' (type: {type(to_email)})")
            logger.info(f"  subject: '{subject}' (type: {type(subject)})")
            logger.info(f"  message length: {len(message) if message else 0}")
            
            # Validate email address
            if not to_email or not to_email.strip():
                logger.error(f"Invalid email address: '{to_email}'")
                return {
                    'success': False,
                    'message': f'Invalid address "{to_email}"'
                }
            
            to_email = to_email.strip()
            
            # Basic email validation
            if '@' not in to_email or '.' not in to_email:
                logger.error(f"Invalid email format: '{to_email}'")
                return {
                    'success': False,
                    'message': f'Invalid email format "{to_email}"'
                }
            
            if settings.EMAIL_BACKEND and 'django' in settings.EMAIL_BACKEND:
                # Use Django's email backend
                result = send_mail(
                    subject=subject,
                    message=message,
                    from_email=self.from_email,
                    recipient_list=[to_email],
                    html_message=html_message,
                    fail_silently=False
                )
                return {
                    'success': bool(result),
                    'message': 'Email sent successfully' if result else 'Failed to send email'
                }
            else:
                # Use direct SMTP
                return self._send_smtp_email(to_email, subject, message, html_message, attachments)
                
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return {
                'success': False,
                'message': f'Email sending failed: {str(e)}'
            }
    
    def _send_smtp_email(
        self, 
        to_email: str, 
        subject: str, 
        message: str, 
        html_message: str = None,
        attachments: List[Dict] = None
    ) -> Dict:
        """Send email using direct SMTP connection"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text part
            text_part = MIMEText(message, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_message:
                html_part = MIMEText(html_message, 'html')
                msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)
            
            # Connect and send
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.use_tls:
                server.starttls()
            
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            
            server.send_message(msg)
            server.quit()
            
            return {
                'success': True,
                'message': 'Email sent successfully via SMTP'
            }
            
        except Exception as e:
            logger.error(f"SMTP email sending failed: {str(e)}")
            return {
                'success': False,
                'message': f'SMTP sending failed: {str(e)}'
            }
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict):
        """Add attachment to email message"""
        try:
            with open(attachment['path'], 'rb') as file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {attachment.get("filename", "attachment")}'
                )
                msg.attach(part)
        except Exception as e:
            logger.error(f"Failed to add attachment: {str(e)}")


class NotificationService:
    """Main service for handling notifications"""
    
    def __init__(self):
        self.email_service = EmailService()
    
    def send_welcome_notification(
        self, 
        user_id: str, 
        email: str, 
        username: str, 
        user_type: str = None
    ) -> Dict:
        """
        Send welcome notification to newly registered user
        
        Args:
            user_id: User ID from auth service (can be integer or UUID string)
            email: User email address
            username: User's username
            user_type: Type of user (PETITIONER, JUDGE, etc.)
        
        Returns:
            Dict with success status and notification details
        """
        try:
            # Normalize user_id to handle both integer and UUID formats
            normalized_user_id = self._normalize_user_id(user_id)
            
            # Check if user wants to receive welcome emails
            preferences = self._get_user_preferences(normalized_user_id, email)
            if not preferences.welcome_emails:
                return {
                    'success': False,
                    'message': 'User has disabled welcome emails'
                }
            
            # Get or create notification type
            notification_type, _ = NotificationType.objects.get_or_create(
                name='welcome_email',
                defaults={
                    'type': 'EMAIL',
                    'template_subject': 'Welcome to Legal Ease Platform',
                    'template_body': 'Welcome to our legal platform!'
                }
            )
            
            # Get welcome email template
            template = self._get_template('WELCOME')
            
            # Prepare template variables
            context_data = {
                'username': username,
                'user_type': user_type or 'User',
                'platform_name': 'Legal Ease',
                'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@legalease.com'),
                'login_url': getattr(settings, 'FRONTEND_LOGIN_URL', 'http://localhost:3000/login'),
                'current_year': timezone.now().year
            }
            
            # Render template
            subject = self._render_template(template.subject, context_data)
            html_message = self._render_template(template.html_body, context_data)
            text_message = self._render_template(template.text_body or self._html_to_text(template.html_body), context_data)
            
            # Create notification record
            notification = Notification.objects.create(
                user_id=user_id,
                email=email,
                notification_type=notification_type,
                template=template,
                subject=subject,
                message=text_message,
                html_message=html_message,
                priority='NORMAL',
                metadata={
                    'username': username,
                    'user_type': user_type,
                    'event_type': 'user_signup'
                }
            )
            
            # Send email
            logger.info(f"About to send email to: '{email}' with subject: '{subject}'")
            result = self.email_service.send_email(
                to_email=email,
                subject=subject,
                message=text_message,
                html_message=html_message
            )
            
            # Update notification status
            if result['success']:
                notification.status = 'SENT'
                notification.sent_at = timezone.now()
            else:
                notification.status = 'FAILED'
                notification.error_message = result['message']
            
            notification.save()
            
            return {
                'success': result['success'],
                'message': result['message'],
                'notification_id': str(notification.id)
            }
            
        except Exception as e:
            logger.error(f"Failed to send welcome notification: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to send welcome notification: {str(e)}'
            }
    
    def send_verification_notification(
        self, 
        user_id: str, 
        email: str, 
        username: str,
        verification_token: str,
        user_type: str = None
    ) -> Dict:
        """
        Send email verification notification
        """
        try:
            # Get or create notification type
            notification_type, _ = NotificationType.objects.get_or_create(
                name='email_verification',
                defaults={
                    'type': 'EMAIL',
                    'template_subject': 'Verify Your Legal Ease Account',
                    'template_body': 'Please verify your email address.'
                }
            )
            
            # Get verification email template
            template = self._get_template('VERIFICATION')
            
            # Prepare template variables
            verification_url = f"{getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000')}/verify-email?token={verification_token}"
            
            context_data = {
                'username': username,
                'verification_url': verification_url,
                'verification_token': verification_token,
                'platform_name': 'Legal Ease',
                'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@legalease.com'),
                'expiry_hours': 24,
                'current_year': timezone.now().year
            }
            logger.info(f"Verification URL: {verification_url}")
            # Render template
            subject = self._render_template(template.subject, context_data)
            html_message = self._render_template(template.html_body, context_data)
            text_message = self._render_template(template.text_body or self._html_to_text(template.html_body), context_data)
            
            # Create notification record
            notification = Notification.objects.create(
                user_id=user_id,
                email=email,
                notification_type=notification_type,
                template=template,
                subject=subject,
                message=text_message,
                html_message=html_message,
                priority='HIGH',
                metadata={
                    'username': username,
                    'user_type': user_type,
                    'event_type': 'email_verification',
                    'verification_token': verification_token
                }
            )
            
            # Send email
            # result = self.email_service.send_email(
            #     to_email=email,
            #     subject=subject,
            #     message=text_message,
            #     html_message=html_message
            # )
            # For testing: skip email sending and return success
            result = {'success': True, 'message': 'Email sending skipped for testing'}
            
            # Update notification status
            if result['success']:
                notification.status = 'SENT'
                notification.sent_at = timezone.now()
            else:
                notification.status = 'FAILED'
                notification.error_message = result['message']
            
            notification.save()
            
            return {
                'success': result['success'],
                'message': result['message'],
                'notification_id': str(notification.id)
            }
            
        except Exception as e:
            logger.error(f"Failed to send verification notification: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to send verification notification: {str(e)}'
            }
    
    def _get_user_preferences(self, user_id: str, email: str) -> NotificationPreference:
        """Get or create user notification preferences"""
        preferences, created = NotificationPreference.objects.get_or_create(
            user_id=user_id,
            defaults={
                'email': email,
                'email_notifications': True,
                'welcome_emails': True,
                'hearing_reminders': True,
                'case_updates': True,
                'document_notifications': True,
                'payment_notifications': True,
            }
        )
        return preferences
    
    def _normalize_user_id(self, user_id: str) -> str:
        """
        Normalize user_id to handle both integer and UUID formats
        For CharField fields, we can store the ID as-is
        """
        return str(user_id).strip('"')  # Remove any extra quotes from JSON parsing
    
    def _get_template(self, template_type: str) -> NotificationTemplate:
        """Get notification template by type"""
        try:
            return NotificationTemplate.objects.get(
                template_type=template_type,
                is_active=True
            )
        except NotificationTemplate.DoesNotExist:
            # Create default template if it doesn't exist
            return self._create_default_template(template_type)
    
    def _create_default_template(self, template_type: str) -> NotificationTemplate:
        """Create default template for the given type"""
        templates = {
            'WELCOME': {
                'name': 'Welcome Email',
                'subject': 'Welcome to {{platform_name}}, {{username}}!',
                'html_body': '''
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Welcome to {{platform_name}}</title>
                </head>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <h1 style="color: #2c3e50;">Welcome to {{platform_name}}!</h1>
                        </div>
                        
                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                            <h2>Hello {{username}},</h2>
                            <p>Welcome to {{platform_name}}, your comprehensive online court hearing platform!</p>
                            <p>As a {{user_type}}, you now have access to a powerful suite of legal tools and services designed to streamline your court proceedings.</p>
                        </div>
                        
                        <div style="margin-bottom: 20px;">
                            <h3>What you can do:</h3>
                            <ul style="padding-left: 20px;">
                                <li>Participate in virtual court hearings</li>
                                <li>Access case documents and files</li>
                                <li>Schedule appointments and consultations</li>
                                <li>Receive real-time notifications about your cases</li>
                                <li>Communicate securely with legal professionals</li>
                            </ul>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{login_url}}" style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Access Your Account</a>
                        </div>
                        
                        <div style="background-color: #e9ecef; padding: 15px; border-radius: 5px; margin-top: 20px;">
                            <p><strong>Need Help?</strong></p>
                            <p>If you have any questions or need assistance, please don't hesitate to contact our support team at <a href="mailto:{{support_email}}">{{support_email}}</a>.</p>
                        </div>
                        
                        <div style="text-align: center; margin-top: 30px; color: #6c757d; font-size: 12px;">
                            <p>&copy; {{current_year}} {{platform_name}}. All rights reserved.</p>
                        </div>
                    </div>
                </body>
                </html>
                ''',
                'text_body': '''
Welcome to {{platform_name}}, {{username}}!

Hello {{username}},

Welcome to {{platform_name}}, your comprehensive online court hearing platform!

As a {{user_type}}, you now have access to a powerful suite of legal tools and services designed to streamline your court proceedings.

What you can do:
- Participate in virtual court hearings
- Access case documents and files
- Schedule appointments and consultations
- Receive real-time notifications about your cases
- Communicate securely with legal professionals

Access your account: {{login_url}}

Need Help?
If you have any questions or need assistance, please contact our support team at {{support_email}}.

© {{current_year}} {{platform_name}}. All rights reserved.
                ''',
                'variables': {
                    'username': 'User\'s display name',
                    'user_type': 'Type of user (Petitioner, Judge, etc.)',
                    'platform_name': 'Platform name',
                    'login_url': 'URL to login page',
                    'support_email': 'Support email address',
                    'current_year': 'Current year'
                }
            },
            'VERIFICATION': {
                'name': 'Email Verification',
                'subject': 'Verify Your {{platform_name}} Account',
                'html_body': '''
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Verify Your Email</title>
                </head>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <h1 style="color: #2c3e50;">Verify Your Email Address</h1>
                        </div>
                        
                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                            <h2>Hello {{username}},</h2>
                            <p>Thank you for registering with {{platform_name}}. To complete your account setup, please verify your email address by clicking the button below.</p>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{verification_url}}" style="background-color: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Verify Email Address</a>
                        </div>
                        
                        <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                            <p><strong>Important:</strong> This verification link will expire in {{expiry_hours}} hours for security reasons.</p>
                        </div>
                        
                        <div style="margin: 20px 0;">
                            <p>If the button above doesn't work, you can also copy and paste the following link into your browser:</p>
                            <p style="word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 3px;">{{verification_url}}</p>
                        </div>
                        
                        <div style="background-color: #e9ecef; padding: 15px; border-radius: 5px; margin-top: 20px;">
                            <p><strong>Need Help?</strong></p>
                            <p>If you didn't create this account or have any questions, please contact our support team at <a href="mailto:{{support_email}}">{{support_email}}</a>.</p>
                        </div>
                        
                        <div style="text-align: center; margin-top: 30px; color: #6c757d; font-size: 12px;">
                            <p>&copy; {{current_year}} {{platform_name}}. All rights reserved.</p>
                        </div>
                    </div>
                </body>
                </html>
                ''',
                'text_body': '''
Verify Your {{platform_name}} Account

Hello {{username}},

Thank you for registering with {{platform_name}}. To complete your account setup, please verify your email address by visiting the following link:

{{verification_url}}

Important: This verification link will expire in {{expiry_hours}} hours for security reasons.

If you didn't create this account or have any questions, please contact our support team at {{support_email}}.

© {{current_year}} {{platform_name}}. All rights reserved.
                ''',
                'variables': {
                    'username': 'User\'s display name',
                    'verification_url': 'Email verification URL',
                    'verification_token': 'Verification token',
                    'platform_name': 'Platform name',
                    'support_email': 'Support email address',
                    'expiry_hours': 'Hours until link expires',
                    'current_year': 'Current year'
                }
            }
        }
        
        template_data = templates.get(template_type, templates['WELCOME'])
        
        return NotificationTemplate.objects.create(
            name=template_data['name'],
            template_type=template_type,
            subject=template_data['subject'],
            html_body=template_data['html_body'],
            text_body=template_data['text_body'],
            variables=template_data['variables'],
            is_active=True
        )
    
    def _render_template(self, template_string: str, context_data: Dict) -> str:
        """Render Django template with context data"""
        try:
            template = Template(template_string)
            context = Context(context_data)
            return template.render(context)
        except Exception as e:
            logger.error(f"Template rendering failed: {str(e)}")
            return template_string
    
    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML to plain text (basic implementation)"""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_content)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


# Convenience function for easy access
def get_notification_service():
    """Get instance of notification service"""
    return NotificationService()
