from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Order , OrderItem
from .forms import ProductForm

@login_required
def dashboard(request):
    if not request.user.is_seller():
        messages.error(request, "Access denied. Seller account required.")
        return redirect('accounts:retail_admin_login')
    
    # Get seller's stats
    total_products = Product.objects.filter(seller=request.user).count()
    active_products = Product.objects.filter(seller=request.user, is_active=True).count()
    low_stock_products = Product.objects.filter(seller=request.user, stock_quantity__lt=5, stock_quantity__gt=0)
    
    # Get orders stats
    total_orders = Order.objects.filter(seller=request.user).count()
    pending_orders = Order.objects.filter(seller=request.user, status='pending').count()
    recent_orders = Order.objects.filter(seller=request.user).order_by('-created_at')[:5]
    
    context = {
        'total_products': total_products,
        'active_products': active_products,
        'low_stock_products': low_stock_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'recent_orders': recent_orders,
    }
    return render(request, 'shop/dashboard.html', context)

@login_required
def order_list(request):
    if not request.user.is_seller():
        messages.error(request, "Access denied. Seller account required.")
        return redirect('accounts:retail_admin_login')
    
    orders = Order.objects.filter(seller=request.user).order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
    }
    return render(request, 'shop/order_list.html', context)

@login_required
def order_detail(request, order_id):
    if not request.user.is_seller():
        messages.error(request, "Access denied. Seller account required.")
        return redirect('accounts:retail_admin_login')
    
    order = get_object_or_404(Order, id=order_id, seller=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'shop/order_detail.html', context)

@login_required
def update_order_status(request, order_id):
    if not request.user.is_seller():
        messages.error(request, "Access denied. Seller account required.")
        return redirect('accounts:retail_admin_login')
    
    order = get_object_or_404(Order, id=order_id, seller=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            old_status = order.status
            order.status = new_status
            order.save()
            messages.success(request, f"Order #{order.order_number} status updated from {old_status} to {new_status}")
        else:
            messages.error(request, "Invalid status selected.")
    
    return redirect('shop:order_detail', order_id=order_id)




@login_required
def product_list(request):
    if not request.user.is_seller():
        messages.error(request, "Access denied. Seller account required.")
        return redirect('accounts:retail_admin_login')
    
    products = Product.objects.filter(seller=request.user)
    
    context = {
        'products': products,
    }
    return render(request, 'shop/product_list.html', context)

@login_required
def add_product(request):
    if not request.user.is_seller():
        messages.error(request, "Access denied. Seller account required.")
        return redirect('accounts:retail_admin_login')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, f"Product '{product.name}' added successfully!")
            return redirect('shop:product_list')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
    }
    return render(request, 'shop/add_product.html', context)

@login_required
def edit_product(request, product_id):
    if not request.user.is_seller():
        messages.error(request, "Access denied. Seller account required.")
        return redirect('accounts:retail_admin_login')
    
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product '{product.name}' updated successfully!")
            return redirect('shop:product_list')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'shop/edit_product.html', context)

@login_required
def delete_product(request, product_id):
    if not request.user.is_seller():
        messages.error(request, "Access denied. Seller account required.")
        return redirect('accounts:retail_admin_login')
    
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    product_name = product.name
    product.delete()
    
    messages.success(request, f"Product '{product_name}' deleted successfully!")
    return redirect('shop:product_list')

