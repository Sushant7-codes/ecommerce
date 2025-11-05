from django.shortcuts import render, redirect
from .forms import RetailAdminRegisterForm, RetailAdminLoginForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .utils import is_email_valid, forgot_password_email
from .models import OTP, CustomUser
from django.contrib.auth.password_validation import validate_password
from django.core.files.uploadedfile import InMemoryUploadedFile

from django.contrib.auth import get_user_model
User = get_user_model()


def retail_admin_register(request):
    if request.method == "POST":
        form = RetailAdminRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data.get("email")

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered. Please login.")
                return redirect("accounts:retail_admin_login")

            try:
                
                from .background_tasks import send_otp
                import random

                otp = random.randint(100000, 999999)

                # Copy cleaned data and remove file objects (can't be serialized)
                pending_data = form.cleaned_data.copy()
                for key, value in list(pending_data.items()):
                    if isinstance(value, InMemoryUploadedFile):
                        pending_data.pop(key)

                # Store only JSON-safe data in session
                request.session["pending_user_data"] = pending_data
                request.session["pending_user_password"] = form.cleaned_data.get("password1")

                # Store OTP in session
                request.session["register_otp"] = str(otp)

                # Send OTP
                send_otp(email, otp, purpose="register")

                messages.success(request, f"OTP sent to {email}. Please verify to complete registration.")
                return redirect("accounts:register_otp_confirmation")

            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
                return redirect("accounts:retail_admin_register")

        else:
            # Invalid form — re-render with errors
            return render(request, "accounts/register.html", {"form": form})

    # GET request — show empty form
    form = RetailAdminRegisterForm()
    return render(request, "accounts/register.html", {"form": form})



def retail_admin_login(request):
    
    if request.method == "POST":
        username=request.POST.get("username")
        password=request.POST.get("password")
    
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("app:dashboard")
            
        messages.error(request, "Invalid username or password")    
        return redirect("accounts:retail_admin_login")
        
    form = RetailAdminLoginForm()
    
    context = {"form": form}
    return render(request, "accounts/login.html", context)

def logout_view(request):
    logout(request)
    return redirect("accounts:retail_admin_login")

def forgot_password(request):
    
    if request.method == "POST":
        email = request.POST.get("email")
        
        if not is_email_valid(email):
            messages.error(request, "Enter a valid email")
            return redirect("accounts:forgot_password")
        
        try:
            forgot_password_email(email)
        except Exception as e:
            messages.error(request, str(e))
            return redirect("accounts:forgot_password")
        
        print(email,"Email sent successfully")
        messages.success(request, "Email sent successfully, please wait for OTP ")
        return redirect("accounts:otp_confirmation")
        
    return render(request, "accounts/forgot-password.html")

def otp_confirmation(request):
    
    if request.method == "POST":
        otp=request.POST.get("otp")
        
        user_id = OTP.check_otp(otp)
        if user_id is None:
            messages.error(request, "Invalid OTP,try again")
            return redirect("accounts:otp_confirmation")  
        
        return redirect("accounts:set_new_password", user_id=user_id)  
        
    return render(request, "accounts/otp-confirmation.html")

def set_new_password(request, user_id=None):
    
    
    if request.method == "POST":
        password1=request.POST.get("password1")
        password2=request.POST.get("password2")
        
        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("accounts:set_new_password",user_id=user_id)
        
        try:
            validate_password(password1)
        except Exception as e:
            for error in list(e):
                messages.error(request, str(error))
            return redirect("accounts:set_new_password",user_id=user_id)
        
        else:
            if user_id is not None:
                user=CustomUser.objects.filter(id=user_id).first()
                
                if user is None:
                    messages.error(request, "User does not exist")
                    return redirect("accounts:set_new_password", user_id=user_id)
                
            user.set_password(password1)
            user.save()
            messages.success(request, "Password changed successfully")
            return redirect("accounts:retail_admin_login")
        
    return render(request, "accounts/new-password.html")


def register_otp_confirmation(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        session_otp = request.session.get("register_otp")
        user_data = request.session.get("pending_user_data")
        user_password = request.session.get("pending_user_password")

        if not (entered_otp and session_otp and user_data):
            messages.error(request, "Session expired. Please register again.")
            return redirect("accounts:retail_admin_register")

        if entered_otp != session_otp:
            messages.error(request, "Invalid OTP. Try again.")
            return redirect("accounts:register_otp_confirmation")

        # ✅ OTP is correct → create user
        user = CustomUser.objects.create_user(
            username=user_data.get("username"),
            email=user_data.get("email"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            address=user_data.get("address"),
            phone_number=user_data.get("phone_number"),
            profile_pic=user_data.get("profile_pic"),
            password=user_password,
        )

        # Clear session
        request.session.pop("pending_user_data", None)
        request.session.pop("pending_user_password", None)
        request.session.pop("register_otp", None)

        messages.success(request, "Account created successfully. You can now log in.")
        return redirect("accounts:retail_admin_login")

    return render(request, "accounts/otp-confirmation.html")
