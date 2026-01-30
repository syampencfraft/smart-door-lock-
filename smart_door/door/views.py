from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.files.base import ContentFile
from .models import User
from .biometrics import verify_face, verify_voice
import hashlib
import base64
import tempfile
import os

# Create your views here.

def index(request):
    return render(request,'index.html')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['confirm']
        
        full_name = request.POST.get('full_name')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        
        profile_image = request.FILES.get('profile_image')
        voice_recording = request.FILES.get('voice_recording')

        if password != confirm:
            return render(request, 'register.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})

        User.objects.create(
            username=username,
            email=email,
            password=hash_password(password),
            full_name=full_name,
            address=address,
            phone_number=phone_number,
            profile_image=profile_image,
            voice_recording=voice_recording
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

    try:
        user = User.objects.get(id=request.session['user_id'])
    except User.DoesNotExist:
        return redirect('login')
        
    return render(request, 'dashboard.html', {'user': user})

def profile(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    return render(request, 'profile.html', {'user': user})

def edit_profile(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    
    if request.method == 'POST':
        user.full_name = request.POST.get('full_name')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')
        user.address = request.POST.get('address')
        
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
        
        if 'voice_recording' in request.FILES:
            user.voice_recording = request.FILES['voice_recording']
            
        user.save()
        return redirect('profile')
        
    return render(request, 'edit_profile.html', {'user': user})

from django.http import JsonResponse
import base64
from django.core.files.base import ContentFile
from .biometrics import verify_face, verify_voice
import tempfile
import os

def verify_biometrics(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    
    if request.method == 'POST':
        auth_type = request.POST.get('type') # 'face' or 'voice'
        
        if auth_type == 'face':
            image_data = request.POST.get('image')
            if not image_data:
                return JsonResponse({'success': False, 'message': 'No image data received'})
            
            # Decode base64 image
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            content = ContentFile(base64.b64decode(imgstr))
            
            reg_img_path = user.profile_image.path if user.profile_image else None
            if not reg_img_path:
                return JsonResponse({'success': False, 'message': 'Registered face image not found'})
            
            match, info = verify_face(reg_img_path, content.read())
            return JsonResponse({'success': match, 'message': info})
            
        elif auth_type == 'voice':
            audio_file = request.FILES.get('audio')
            if not audio_file:
                return JsonResponse({'success': False, 'message': 'No audio data received'})
            
            reg_voice_path = user.voice_recording.path if user.voice_recording else None
            if not reg_voice_path:
                return JsonResponse({'success': False, 'message': 'Registered voice sample not found'})
            
            # Save live audio to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                for chunk in audio_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name
            
            match, info = verify_voice(reg_voice_path, tmp_path)
            os.unlink(tmp_path)
            
            return JsonResponse({'success': match, 'message': info})
            
    return render(request, 'verify_biometrics.html', {'user': user})

def logout_view(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('login')
