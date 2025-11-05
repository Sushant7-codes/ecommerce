from django.db import models
import random
import string

# Create your models here.

def generate_unique_barcode():
    """Generate a unique 10-digit barcode"""
    while True:
        code = ''.join(random.choices(string.digits, k=10))
        # Check if this barcode already exists in Item or Price model
        if not Item.objects.filter(barcode=code).exists() and not Price.objects.filter(barcode=code).exists():
            return code

class Shop(models.Model):
    admin_user = models.OneToOneField("accounts.CustomUser", on_delete=models.CASCADE, related_name='shop')
    name = models.CharField(max_length=255)
    code=models.CharField(max_length=10, unique=True, blank=True, null=True)
    slug = models.SlugField(unique=True,blank=True, null=True)
    owner_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255)
    city=models.CharField(max_length=50)
    state=models.CharField(max_length=50)
    country=models.CharField(max_length=50)
    postal_code=models.CharField(max_length=50)
    map_location_url=models.URLField(blank=True, null=True)
    
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    logo = models.ImageField(upload_to="shop_logos/", blank=True, null=True)
    banner = models.ImageField(upload_to="shop_banners/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    updated_at = models.DateTimeField(auto_now=True)
    established_date = models.DateField(blank=True, null=True)
    
    
    def __str__(self):
        return self.name 
    
class Item(models.Model):
    name=models.CharField(max_length=100)
    shop=models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='items')
    barcode = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    
    class Meta:
        unique_together = ('name', 'shop')
        
    def save(self, *args, **kwargs):
        if not self.barcode:
            self.barcode = generate_unique_barcode()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.name} | {self.shop}" 
    
class Price(models.Model):
    name=models.CharField(max_length=100)
    amount=models.DecimalField(max_digits=10, decimal_places=2)
    item=models.ForeignKey(Item, on_delete=models.CASCADE, related_name='prices')
    stock=models.PositiveIntegerField(default=1)
    barcode = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    class Meta:
        unique_together = ('name', 'item')
        
    def save(self, *args, **kwargs):
        if not self.barcode:
            self.barcode = generate_unique_barcode()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.name} | {self.item}" 