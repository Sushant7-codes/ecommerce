import stripe 

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Cart, CartItem
from shop.models import Product, Order, OrderItem


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
    # Get recent orders for the dashboard
    recent_orders = Order.objects.filter(customer=request.user).order_by('-created_at')[:3]
    
    context = {
        'featured_products': featured_products,
        'recent_orders': recent_orders,
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

# CHECKOUT VIEWS
# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def checkout(request):
    if not request.user.is_buyer():
        messages.error(request, "Access denied. Buyer account required.")
        return redirect('accounts:retail_admin_login')
    
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        messages.error(request, "Your cart is empty. Add some items to checkout.")
        return redirect('buyer:cart')
    
    # Handle selected items
    selected_items_param = request.GET.get('selected_items', '')
    if selected_items_param:
        selected_item_ids = [int(id) for id in selected_items_param.split(',') if id.isdigit()]
        cart_items = cart.items.filter(id__in=selected_item_ids)
    else:
        cart_items = cart.items.all()
    
    # Check stock availability
    for item in cart_items:
        if item.quantity > item.product.stock_quantity:
            messages.error(request, f"Sorry, only {item.product.stock_quantity} units of {item.product.name} are available.")
            return redirect('buyer:cart')
    
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        customer_phone = request.POST.get('customer_phone')
        customer_email = request.POST.get('customer_email')
        payment_method = request.POST.get('payment_method')
        
        # Validate required fields
        if not all([shipping_address, customer_phone, customer_email, payment_method]):
            messages.error(request, "Please fill all required fields.")
            return render(request, 'buyer/checkout.html', {'cart': cart})
        
        # Get selected items from POST
        selected_items_param = request.POST.get('selected_items', '')
        if selected_items_param:
            selected_item_ids = [int(id.strip()) for id in selected_items_param.split(',') if id.strip().isdigit()]
            cart_items = cart.items.filter(id__in=selected_item_ids)
        else:
            cart_items = cart.items.all()
        
        if not cart_items.exists():
            messages.error(request, "No items selected for checkout.")
            return render(request, 'buyer/checkout.html', {'cart': cart})
        
        # Calculate total amount
        total_amount = sum(item.total_price() for item in cart_items)
        
        try:
            # Get the seller from the first product
            first_product_seller = cart_items.first().product.seller
            
            # Create order
            order = Order.objects.create(
                customer=request.user,
                seller=first_product_seller,
                total_amount=total_amount,
                shipping_address=shipping_address,
                customer_phone=customer_phone,
                status='pending'
            )
            
            # Create order items and update stock
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                
                # Update product stock
                product = cart_item.product
                product.stock_quantity -= cart_item.quantity
                product.save()
            
            # Handle payment method
            if payment_method == 'cod':
                # Cash on Delivery
                cart_items.delete()
                messages.success(request, "Order placed successfully! Pay when you receive your order.")
                return redirect('buyer:checkout_success', order_number=order.order_number)
                
            elif payment_method == 'stripe':
                # SIMULATED STRIPE PAYMENT - FOR TESTING
                # Instead of real Stripe, we'll simulate the payment flow
                
                # Store a fake session ID
                import random
                import string
                fake_session_id = 'cs_test_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=24))
                order.stripe_session_id = fake_session_id
                order.save()
                
                # Remove items from cart
                cart_items.delete()
                
                # Show a simulated Stripe payment page
                return render(request, 'buyer/stripe_simulation.html', {
                    'order': order,
                    'total_amount': total_amount,
                    'customer_email': customer_email
                })
            
        except Exception as e:
            messages.error(request, f"Error creating order: {str(e)}")
            return render(request, 'buyer/checkout.html', {'cart': cart})
    
    context = {
        'cart': cart,
    }
    return render(request, 'buyer/checkout.html', context)

@login_required
def checkout_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    
    # Check if this is a Stripe payment
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            # Verify the Stripe payment
            stripe_session = stripe.checkout.Session.retrieve(session_id)
            
            if stripe_session.payment_status == 'paid':
                order.status = 'paid'
                order.save()
                messages.success(request, "Payment successful! Your order has been confirmed.")
            else:
                messages.warning(request, "Payment pending. Your order will be processed once payment is confirmed.")
                
        except Exception as e:
            messages.info(request, "Order received! Payment verification in progress.")
    
    context = {
        'order': order,
    }
    return render(request, 'buyer/checkout_success.html', context)


@login_required
def checkout_cancel(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    
    # Mark order as cancelled if it was a Stripe payment that failed
    if order.stripe_session_id and order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        messages.info(request, "Payment was cancelled. Your order has been cancelled.")
    else:
        messages.info(request, "Checkout was cancelled.")
    
    return redirect('buyer:cart')

@login_required
def order_history(request):
    if not request.user.is_buyer():
        messages.error(request, "Access denied. Buyer account required.")
        return redirect('accounts:retail_admin_login')
    
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'buyer/order_history.html', context)

@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    context = {
        'order': order,
    }
    return render(request, 'buyer/order_detail.html', context)

# Dummy payment webhook for Stripe simulation
@csrf_exempt
@login_required
def stripe_webhook(request):
    """Simulate Stripe payment webhook"""
    if request.method == 'POST':
        # In a real implementation, you'd verify the Stripe signature
        # For now, we'll just simulate a successful payment
        return JsonResponse({'status': 'success'})
    
    
@login_required
def stripe_payment_complete(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    
    # Mark order as paid
    order.status = 'paid'
    order.save()
    
    messages.success(request, "Payment successful! Your order has been confirmed.")
    return redirect('buyer:checkout_success', order_number=order.order_number)