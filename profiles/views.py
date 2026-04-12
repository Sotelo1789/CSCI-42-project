from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required
def my_profile_view(request):
    profile = None
    if request.user.is_business:
        profile = getattr(request.user, 'business_profile', None)
    elif request.user.is_consumer:
        profile = getattr(request.user, 'consumer_profile', None)
    return render(request, 'profiles/my_profile.html', {'profile': profile})


@login_required
def edit_profile_view(request):
    user = request.user
    profile = None
    if user.is_business:
        profile = getattr(user, 'business_profile', None)
    elif user.is_consumer:
        profile = getattr(user, 'consumer_profile', None)

    if request.method == 'POST':
        # ── Account fields (both types) ──
        contact_number = request.POST.get('contact_number', '').strip()
        user.contact_number = contact_number

        if user.is_business and profile:
            profile.business_name    = request.POST.get('business_name', '').strip()
            profile.business_address = request.POST.get('business_address', '').strip()
            profile.tin              = request.POST.get('tin', '').strip()
            profile.business_type    = request.POST.get('business_type', '').strip()
            profile.rep_name         = request.POST.get('rep_name', '').strip()
            profile.rep_position     = request.POST.get('rep_position', '').strip()
            profile.rep_contact      = request.POST.get('rep_contact', '').strip()
            profile.save()

        elif user.is_consumer and profile:
            profile.full_name = request.POST.get('full_name', '').strip()
            profile.address   = request.POST.get('address', '').strip()
            profile.save()

        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profiles:my_profile')

    return render(request, 'profiles/edit_profile.html', {'profile': profile})
