from background_task import background
from django.conf import settings
from django.core.mail import send_mail


@background(schedule=3)
def send_otp(email, new_otp, purpose="forgot"):
    if purpose == "register":
        subject = "Verify Your Email - Registration"
        message = f"""
        Welcome! 🎉
        
        Use the OTP {new_otp} to verify your email and complete registration.
        
        This OTP will expire in 5 minutes.
        """
    else:  # default → forgot password
        subject = "Password Reset OTP"
        message = f"""
        You requested to reset your password.
        
        Use the OTP {new_otp} to reset your password
        OR
        Go to the OTP confirmation page: http://127.0.0.1:8000/accounts/otp-confirmation/
        
        This OTP will expire in 5 minutes.
        """

    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
