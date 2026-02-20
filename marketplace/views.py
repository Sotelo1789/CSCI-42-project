from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def marketplace_view(request):
    # TODO: Implement marketplace
    return render(request, 'marketplace/marketplace.html')
