from django.shortcuts import render, redirect
from django.http import HttpResponse

ADMIN_USERNAME = 'jagdish'
ADMIN_PASSWORD = 'jagdish@123'

def admin_login(request):
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            request.session['is_admin'] = True
            return redirect('/')
        else:
            error = 'Invalid username or password.'
    return render(request, 'admin_login.html', {'error': error})

def admin_logout(request):
    request.session.flush()
    return redirect('admin_login') 