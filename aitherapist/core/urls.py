# core/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main app features
    path('chat/', views.chat_view, name='chat'),
    path('chat/new/', views.new_chat, name='new_chat'),
    path('chat/clear/', views.clear_chat, name='clear_chat'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('deleteAcc/', views.deleteAcc_view, name='deleteAcc'),
    
    # endpoints
    path('send-message/', views.send_message, name='send_message'),
    path('api/coping-strategy/', views.get_coping_strategy, name='get_coping_strategy'),
]