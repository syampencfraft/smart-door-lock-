from django.urls import path
from . import views

urlpatterns = [

    path('',views.index),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('verify-biometrics/', views.verify_biometrics, name='verify_biometrics'),
]
