from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request,'index.html')

from django.shortcuts import render, redirect
from .models import User
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['confirm']

        if password != confirm:
            return render(request, 'register.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})

        User.objects.create(
            username=username,
            email=email,
            password=hash_password(password)
        )
        return redirect('login')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = hash_password(request.POST['password'])

        try:
            user = User.objects.get(username=username, password=password)
            if not user.is_approved:
                return render(request, 'login.html', {'error': 'Admin approval pending'})
            request.session['user_id'] = user.id
            return redirect('dashboard')
        except:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

def dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    return render(request, 'dashboard.html', {'user': user})
