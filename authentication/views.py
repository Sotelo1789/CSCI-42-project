from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'authentication/login.html', {'username': username})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'authentication/login.html', {'username': username})

    return render(request, 'authentication/login.html')


def logout_view(request):
    logout(request)
    return redirect('authentication:login')


def register_view(request):
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
