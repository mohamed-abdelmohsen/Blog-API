from django.urls import path
from . import views

urlpatterns = [
    # Custom authentication views
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('logout-all/', views.LogoutAllView.as_view(), name='logout-all'),
    path('refresh/', views.RefreshTokenView.as_view(), name='refresh-token'),
    
    # User profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
]