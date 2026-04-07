from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def marketplace_view(request):
    # TODO: Implement marketplace
    return render(request, 'marketplace/marketplace.html')

def create_listing_view(request):
    return render(request, 'marketplace/create_listing.html')

def respond_to_request_view(request):
    return render(request, 'marketplace/business_response.html')
