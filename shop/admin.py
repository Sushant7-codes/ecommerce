from django.contrib import admin
from shop.models import Shop, Item, Price

# Register your models here.
admin.site.register(Shop)
admin.site.register(Item)
admin.site.register(Price)