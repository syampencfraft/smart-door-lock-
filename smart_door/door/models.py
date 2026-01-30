from django.db import models

# Create your models here.
from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profiles/images/', null=True, blank=True)
    voice_recording = models.FileField(upload_to='profiles/voices/', null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.username
