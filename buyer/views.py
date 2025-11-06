from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, CartItem, Order
from shop.models import Product
from django.http import JsonResponse

@login_required
def dashboard(request):
    # Allow both buyers and sellers to see the homepage
    # Remove the buyer-only restriction
    featured_products = Product.objects.filter(is_active=True)[:8]
    
    context = {
        'featured_products': featured_products,
    }
    return render(request, 'buyer/dashboard.html', context)

@login_required
def product_list(request):
    # Allow both buyers and sellers to browse products
    # Remove the buyer-only restriction
    products = Product.objects.filter(is_active=True)
    
    context = {
        'products': products,
    }
    return render(request, 'buyer/product_list.html', context)

@login_required
def cart_view(request):
    # KEEP this buyer-only - sellers shouldn't use cart
    if not request.user.is_buyer():
        messages.error(request, "Access denied. Buyer account required.")
        return redirect('accounts:retail_admin_login')
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    context = {
        'cart': cart,
    }
    return render(request, 'buyer/cart.html', context)

@login_required
def add_to_cart(request, product_id):
    # KEEP this buyer-only
    if not request.user.is_buyer():
        messages.error(request, "Access denied. Buyer account required.")
        return redirect('buyer:product_list')  # Redirect to products instead of login
    
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f"{product.name} added to cart!")
    return redirect('buyer:product_list')

@login_required
def remove_from_cart(request, item_id):
    # KEEP this buyer-only
    if not request.user.is_buyer():
        messages.error(request, "Access denied.")
        return redirect('buyer:product_list')  # Redirect to products instead of login
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    
    messages.success(request, f"{product_name} removed from cart!")
    return redirect('buyer:cart')