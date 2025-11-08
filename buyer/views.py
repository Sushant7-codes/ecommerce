from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Cart, CartItem
from shop.models import Product

def root_redirect(request):
    """Smart redirect based on user type"""
    if request.user.is_authenticated:
        if request.user.is_seller():
            return redirect('shop:dashboard')
        elif request.user.is_buyer():
            return redirect('buyer:dashboard')
    return redirect('buyer:dashboard')

@login_required
def dashboard(request):
    featured_products = Product.objects.filter(is_active=True)[:8]
    context = {
        'featured_products': featured_products,
    }
    return render(request, 'buyer/dashboard.html', context)

@login_required
def product_list(request):
    products = Product.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    context = {
        'products': products,
    }
    return render(request, 'buyer/product_list.html', context)

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    context = {
        'product': product,
    }
    return render(request, 'buyer/product_detail.html', context)

@login_required
def cart_view(request):
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
    if not request.user.is_buyer():
        messages.error(request, "Access denied. Buyer account required.")
        return redirect('buyer:product_list')
    
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if item already in cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"Added another {product.name} to cart!")
    else:
        messages.success(request, f"{product.name} added to cart!")
    
    return redirect('buyer:product_list')

@login_required
def remove_from_cart(request, item_id):
    if not request.user.is_buyer():
        messages.error(request, "Access denied.")
        return redirect('buyer:product_list')
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    
    messages.success(request, f"{product_name} removed from cart!")
    return redirect('buyer:cart')

# NEW VIEWS FOR ENHANCED CART FUNCTIONALITY
@login_required
def update_cart_item_quantity(request, item_id):
    """Update quantity for a specific cart item with stock validation"""
    if not request.user.is_buyer():
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        action = request.POST.get('action')
        
        if action == 'increase':
            # Check if quantity exceeds available stock
            if cart_item.quantity >= cart_item.product.stock_quantity:
                return JsonResponse({
                    'success': False,
                    'error': f'Only {cart_item.product.stock_quantity} items available in stock'
                }, status=400)
            cart_item.quantity += 1
        elif action == 'decrease' and cart_item.quantity > 1:
            cart_item.quantity -= 1
        
        cart_item.save()
        
        return JsonResponse({
            'success': True,
            'quantity': cart_item.quantity,
            'item_total': float(cart_item.total_price()),
            'cart_total': float(cart_item.cart.total_price()),
            'max_stock': cart_item.product.stock_quantity
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
@login_required
def remove_single_quantity(request, item_id):
    """Remove one quantity of an item"""
    if not request.user.is_buyer():
        messages.error(request, "Access denied.")
        return redirect('buyer:cart')
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        messages.success(request, f"Removed one {product_name} from cart!")
    else:
        cart_item.delete()
        messages.success(request, f"{product_name} removed from cart!")
    
    return redirect('buyer:cart')