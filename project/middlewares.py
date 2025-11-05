from django.shortcuts import redirect

class AccountsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        
        restricted_paths = ["/accounts/login/", "/accounts/register/"]
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.user.is_authenticated and request.path in restricted_paths:
            return redirect("app:dashboard")
            
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response