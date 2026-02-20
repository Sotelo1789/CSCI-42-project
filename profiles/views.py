from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def my_profile_view(request):
    return render(request, 'profiles/my_profile.html')


@login_required
def edit_profile_view(request):
    # TODO: Handle profile edits
    return render(request, 'profiles/edit_profile.html')
