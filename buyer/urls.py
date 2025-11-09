from django.urls import path
from . import views

app_name = "buyer"

urlpatterns = [
    path('', views.root_redirect, name='root_redirect'),
    path('home/', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    # NEW URLS FOR ENHANCED CART
    path('update-quantity/<int:item_id>/', views.update_cart_item_quantity, name='update_quantity'),
    path('remove-single/<int:item_id>/', views.remove_single_quantity, name='remove_single'),
    # CHECKOUT URLS
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/success/<str:order_number>/', views.checkout_success, name='checkout_success'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
    
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/success/<str:order_number>/', views.checkout_success, name='checkout_success'),
    path('checkout/cancel/<str:order_number>/', views.checkout_cancel, name='checkout_cancel'),
    
    path('stripe-payment/complete/<str:order_number>/', views.stripe_payment_complete, name='stripe_payment_complete'),
]