from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category

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
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        stock_quantity = request.POST.get('stock_quantity')
        image = request.FILES.get('image')
        
        category = get_object_or_404(Category, id=category_id)
        
        product = Product(
            name=name,
            description=description,
            price=price,
            category=category,
            seller=request.user,
            stock_quantity=stock_quantity,
            image=image
        )
        product.save()
        
        messages.success(request, f"Product '{name}' added successfully!")
        return redirect('shop:product_list')
    
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'shop/add_product.html', context)

@login_required
def edit_product(request, product_id):
    if not request.user.is_seller():
        messages.error(request, "Access denied. Seller account required.")
        return redirect('accounts:retail_admin_login')
    
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.category_id = request.POST.get('category')
        product.stock_quantity = request.POST.get('stock_quantity')
        
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
        
        product.save()
        messages.success(request, f"Product '{product.name}' updated successfully!")
        return redirect('shop:product_list')
    
    categories = Category.objects.all()
    context = {
        'product': product,
        'categories': categories,
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
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        category = Category(name=name, description=description)
        category.save()
        
        messages.success(request, f"Category '{name}' added successfully!")
        return redirect('shop:category_list')
    
    context = {
        'categories': categories,
    }
    return render(request, 'shop/category_list.html', context)