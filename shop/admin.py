from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'seller', 'price', 'stock_quantity', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    list_per_page = 20
    
    def get_queryset(self, request):
        # Show all products to admin (not filtered by seller)
        return super().get_queryset(request)