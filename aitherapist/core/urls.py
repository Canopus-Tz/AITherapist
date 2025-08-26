# core/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main app features
    path('chat/', views.chat_view, name='chat'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('deleteAcc/', views.deleteAcc_view, name='deleteAcc'),
    
    # AJAX endpoints
    path('send-message/', views.send_message, name='send_message'),
    path('api/coping-strategy/', views.get_coping_strategy, name='get_coping_strategy'),
]