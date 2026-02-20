from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    # TODO: Implement login logic
    return render(request, 'authentication/login.html')


def logout_view(request):
    logout(request)
    return redirect('authentication:login')


def register_view(request):
    # Choose account type
    return render(request, 'authentication/register.html')


def register_business_view(request):
    # TODO: Implement business registration
    return render(request, 'authentication/register_business.html')


def register_consumer_view(request):
    # TODO: Implement consumer registration
    return render(request, 'authentication/register_consumer.html')


def reset_password_view(request):
    # TODO: Implement send OTP
    return render(request, 'authentication/reset_password.html')


def verify_otp_view(request):
    # TODO: Implement OTP verification + password change
    return render(request, 'authentication/verify_otp.html')
