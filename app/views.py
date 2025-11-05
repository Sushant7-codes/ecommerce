from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from shop.forms import ShopForm
from django.urls import reverse_lazy


@login_required
def dashboard(request):
    
    try:
        request.user.shop
    except Exception as e:
        print(e)
        message=(
            "Welcome to the dashboard, please create a shop to get started !"
        )
        messages.info(request, message)
        
        shop_res_form = ShopForm()
        form_submission_url=reverse_lazy("shop:shop_register")
        context={"form":shop_res_form, "form_submission_url":form_submission_url}
        return render(request, "app/dashboard.html", context)
    
    return render(request, "app/dashboard.html")