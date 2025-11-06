from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    
    class Roles(models.TextChoices):
        BUYER = "buyer", "Buyer"
        SELLER = "seller", "Seller"
        
    address = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    profile_pic = models.ImageField(upload_to="profile_pics", null=True, blank=True)
    
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.BUYER,
    )
    
    # REMOVE or COMMENT OUT the workplace field for now
    # workplace = models.ForeignKey(
    #     'shop.Shop', 
    #     on_delete=models.CASCADE, 
    #     null=True, 
    #     blank=True,
    #     related_name='staff_members'
    # )
    
    def is_buyer(self):
        return self.role == self.Roles.BUYER
    
    def is_seller(self):
        return self.role == self.Roles.SELLER
    
    def __str__(self):
        return self.username

# OTP model remains the same...
class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @staticmethod
    def generate_otp(email):
        import random
        
        user = CustomUser.objects.filter(email=email).first()
        if user is None:
            raise Exception("User does not exist")
        
        for _ in range(3):
            otp = random.randint(100000, 999999)
            if not OTP.objects.filter(otp=otp).exists():
                break 
            
        new_otp = OTP(user=user, otp=otp)
        new_otp.save()
        return new_otp.otp

    def is_expired(self):
        from django.utils import timezone
        import datetime
        
        now = timezone.now()
        return now - self.created_at > datetime.timedelta(minutes=5)
        
    @staticmethod
    def check_otp(otp_value):
        otp_record = OTP.objects.filter(otp=otp_value).first()
        if otp_record and not otp_record.is_expired():
            user_id = otp_record.user.id
            otp_record.delete()
            return user_id
        return None        
        
    def __str__(self):
        return self.otp