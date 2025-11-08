from django.contrib import admin
from .models import Product, Order, OrderItem  # ADD Order and OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'seller', 'price', 'stock_quantity', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'seller']  # ADD seller to filters
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    list_per_page = 20
    list_editable = ['price', 'stock_quantity', 'is_active']  # ADD this for quick editing
    
    def get_queryset(self, request):
        # Show all products to admin (not filtered by seller)
        return super().get_queryset(request)

# ADD these new admin classes for Order and OrderItem
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'seller', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'seller']  # ADD filters
    search_fields = ['order_number', 'customer__username', 'seller__username']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    list_editable = ['status']  # ADD for quick status updates

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'item_total']
    list_filter = ['order__status']  # ADD filter by order status
    search_fields = ['product__name', 'order__order_number']
    readonly_fields = []  # No readonly fields needed
    list_per_page = 20
    autocomplete_fields = ['product', 'order']  # ADD for better selection