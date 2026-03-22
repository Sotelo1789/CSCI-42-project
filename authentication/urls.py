app_name = "authentication"
from django.urls import path
from . import views



urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('register/business/', views.register_business_view, name='register_business'),
    path('register/consumer/', views.register_consumer_view, name='register_consumer'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
]
