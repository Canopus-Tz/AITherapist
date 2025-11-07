# core/email_utils.py
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_otp_email(user, email, otp_code):
    """Send OTP verification email to user"""
    subject = 'AI Therapist - Email Verification Code'
    
    # Create email message
    message = f"""
Hello {user.username},

Thank you for registering with AI Therapist!

Your email verification code is: {otp_code}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

Best regards,
AI Therapist Team
"""
    
    try:
        # Determine from_email
        from_email = 'noreply@aitherapist.com'
        if hasattr(settings, 'DEFAULT_FROM_EMAIL') and settings.DEFAULT_FROM_EMAIL:
            from_email = settings.DEFAULT_FROM_EMAIL
        elif hasattr(settings, 'EMAIL_HOST_USER') and settings.EMAIL_HOST_USER:
            from_email = settings.EMAIL_HOST_USER
        
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

