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
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('door-unlocked/', views.door_unlocked, name='door_unlocked'),
]
