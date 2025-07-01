from django.shortcuts import render, redirect
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

ADMIN_USERNAME = 'jagdish'
ADMIN_PASSWORD = 'jagdish@123'
VIEWER_USERNAME = 'viewer'
VIEWER_PASSWORD = 'viewer@123'

def admin_login(request):
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            request.session['is_authenticated'] = True
            request.session['role'] = 'admin'
            logger.warning("Logged in as admin. Session: %s", dict(request.session))
            return redirect('/')
        elif username == VIEWER_USERNAME and password == VIEWER_PASSWORD:
            request.session['is_authenticated'] = True
            request.session['role'] = 'viewer'
            logger.warning("Logged in as viewer. Session: %s", dict(request.session))
            return redirect('/')
        else:
            error = 'Invalid username or password.'
    return render(request, 'admin_login.html', {'error': error})

def admin_logout(request):
    request.session.flush()
    return redirect('admin_login') 