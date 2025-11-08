from django.urls import path
from . import views

app_name = "buyer"

urlpatterns = [
    path('', views.root_redirect, name='root_redirect'),  # NEW: Smart redirect
    path('home/', views.dashboard, name='dashboard'),  # CHANGED: Moved dashboard to /home/
    path('products/', views.product_list, name='product_list'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
]