from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CustomUserProfileView
from . import views
app_name = 'users'

urlpatterns = [
    path('login/',auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('profile/', CustomUserProfileView.as_view(template_name='users/profile.html'), name='profile'),

    # path('join/', views.SignupView.as_view(), name='join'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

]