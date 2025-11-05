from django.shortcuts import redirect

class AccountsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of paths that don't require authentication
        public_paths = [
            '/accounts/login/',
            '/accounts/register/',
            '/accounts/forgot-password/',
            '/accounts/otp-confirmation/',
            '/admin/',
        ]
        
        # Check if user is authenticated and trying to access restricted area
        if not request.user.is_authenticated and not any(request.path.startswith(path) for path in public_paths):
            return redirect('accounts:retail_admin_login')
        
        # If user is authenticated and tries to access login/register, redirect to appropriate dashboard
        if request.user.is_authenticated and request.path in ['/accounts/login/', '/accounts/register/']:
            if request.user.is_seller():
                return redirect('shop:dashboard')
            else:
                return redirect('buyer:dashboard')
        
        response = self.get_response(request)
        return response