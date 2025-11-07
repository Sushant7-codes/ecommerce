from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category
from .forms import ProductForm, CategoryForm  # Add this import

@login_required
def dashboard(request):
    if not request.user.is_seller():
        messages.error(request, "Access denied. Seller account required.")
        return redirect('accounts:retail_admin_login')
    
    # Get seller's stats
    total_products = Product.objects.filter(seller=request.user).count()
    active_products = Product.objects.filter(seller=request.user, is_active=True).count()
    low_stock_products = Product.objects.filter(seller=request.user, stock_quantity__lt=5, stock_quantity__gt=0)
    
    context = {
        'total_products': total_products,
        'active_products': active_products,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'shop/dashboard.html', context)

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

@login_required
def category_list(request):
    if not request.user.is_seller():
        messages.error(request, "Access denied. Seller account required.")
        return redirect('accounts:retail_admin_login')
    
    categories = Category.objects.all()
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{form.cleaned_data['name']}' added successfully!")
            return redirect('shop:category_list')
    else:
        form = CategoryForm()
    
    context = {
        'categories': categories,
        'form': form,
    }
    return render(request, 'shop/category_list.html', context)