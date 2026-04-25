from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import transaction
from .models import Client, BusinessProfile, ConsumerProfile


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
    """Step 1: Choose account type."""
    return render(request, 'authentication/register.html')


def register_business_view(request):
    """Step 2a: Business registration form."""
    if request.method == 'POST':
        # ── Account fields ──
        username       = request.POST.get('username', '').strip()
        email          = request.POST.get('email', '').strip()
        password       = request.POST.get('password', '')
        confirm_pw     = request.POST.get('confirm_password', '')
        contact_number = request.POST.get('contact_number', '').strip()

        # ── Business profile fields ──
        business_name    = request.POST.get('business_name', '').strip()
        business_address = request.POST.get('business_address', '').strip()
        tin              = request.POST.get('tin', '').strip()
        business_type    = request.POST.get('business_type', '').strip()
        rep_name         = request.POST.get('rep_name', '').strip()
        rep_position     = request.POST.get('rep_position', '').strip()
        rep_contact      = request.POST.get('rep_contact', '').strip()

        # ── Uploaded documents ──
        mayors_permit   = request.FILES.get('mayors_permit')
        sec_certificate = request.FILES.get('sec_certificate')
        bir_certificate = request.FILES.get('bir_certificate')
        tax_clearance   = request.FILES.get('tax_clearance')
        other_documents = request.FILES.get('other_documents')

        # ── Validation ──
        errors = []
        if not username:   errors.append('Username is required.')
        if not email:      errors.append('Email is required.')
        if not password:   errors.append('Password is required.')
        if password != confirm_pw:
            errors.append('Passwords do not match.')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if Client.objects.filter(username=username).exists():
            errors.append('Username already taken.')
        if Client.objects.filter(email=email).exists():
            errors.append('An account with this email already exists.')
        if not business_name:    errors.append('Business name is required.')
        if not business_address: errors.append('Business address is required.')
        if not tin:              errors.append('TIN is required.')
        if not business_type:    errors.append('Business type is required.')
        if not rep_name:         errors.append('Representative name is required.')
        if not rep_position:     errors.append('Representative position is required.')
        if not rep_contact:      errors.append('Representative contact is required.')
        if not mayors_permit:    errors.append("Mayor's Permit is required.")
        if not sec_certificate:  errors.append('SEC Certificate is required.')
        if not bir_certificate:  errors.append('BIR Certificate is required.')
        if not tax_clearance:    errors.append('Tax Clearance is required.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'authentication/register_business.html', {
                'form_data': request.POST
            })

        # ── Save ──
        try:
            with transaction.atomic():
                client = Client.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    account_type='business',
                    contact_number=contact_number,
                )
                BusinessProfile.objects.create(
                    client=client,
                    business_name=business_name,
                    business_address=business_address,
                    tin=tin,
                    business_type=business_type,
                    rep_name=rep_name,
                    rep_position=rep_position,
                    rep_contact=rep_contact,
                    mayors_permit=mayors_permit,
                    sec_certificate=sec_certificate,
                    bir_certificate=bir_certificate,
                    tax_clearance=tax_clearance,
                    other_documents=other_documents,
                    status='pending',
                )
            messages.success(request,
                'Registration submitted! Your account is pending admin approval.')
            return redirect('authentication:login')

        except Exception as e:
            messages.error(request, f'Registration failed: {e}')
            return render(request, 'authentication/register_business.html', {
                'form_data': request.POST
            })
    return render(request, 'authentication/register_business.html')


def register_consumer_view(request):
    """Step 2b: Consumer registration form."""
    if request.method == 'POST':
        username       = request.POST.get('username', '').strip()
        email          = request.POST.get('email', '').strip()
        password       = request.POST.get('password', '')
        confirm_pw     = request.POST.get('confirm_password', '')
        contact_number = request.POST.get('contact_number', '').strip()
        full_name      = request.POST.get('full_name', '').strip()
        address        = request.POST.get('address', '').strip()
        government_id  = request.FILES.get('government_id')

        errors = []
        if not username:  errors.append('Username is required.')
        if not email:     errors.append('Email is required.')
        if not password:  errors.append('Password is required.')
        if password != confirm_pw:
            errors.append('Passwords do not match.')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if Client.objects.filter(username=username).exists():
            errors.append('Username already taken.')
        if Client.objects.filter(email=email).exists():
            errors.append('An account with this email already exists.')
        if not full_name:     errors.append('Full name is required.')
        if not address:       errors.append('Address is required.')
        if not government_id: errors.append('A government-issued ID (JPEG) is required.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'authentication/register_consumer.html', {
                'form_data': request.POST
            })

        try:
            with transaction.atomic():
                client = Client.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    account_type='consumer',
                    contact_number=contact_number,
                )
                ConsumerProfile.objects.create(
                    client=client,
                    full_name=full_name,
                    address=address,
                    government_id=government_id,
                )
            messages.success(request, 'Account created! You can now log in.')
            return redirect('authentication:login')

        except Exception as e:
            messages.error(request, f'Registration failed: {e}')
            return render(request, 'authentication/register_consumer.html', {
                'form_data': request.POST
            })

    return render(request, 'authentication/register_consumer.html')