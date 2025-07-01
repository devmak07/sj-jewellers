from django.shortcuts import redirect
from django.urls import reverse

class AdminAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed_paths = [reverse('admin_login'), reverse('admin_logout')]
        if not request.session.get('is_admin') and request.path not in allowed_paths:
            if request.path == '/':
                return redirect('admin_login')
            return redirect('admin_login')
        response = self.get_response(request)
        return response 