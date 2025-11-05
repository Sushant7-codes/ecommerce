from .background_tasks import send_otp

def is_email_valid(email):
    from django.core.validators import validate_email

    try:
        validate_email(email)
        return True
    except Exception :
        return False
    

def forgot_password_email(email):
    from .models import OTP
    
    try:
        new_otp = OTP.generate_otp(email)
    except Exception as e:
        raise Exception(str(e))
    
    send_otp(email,new_otp)
