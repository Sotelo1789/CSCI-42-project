from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CreateListing, RespondToRequest
from .models import Listing, ListingImage


def isBusiness(request):
    if hasattr(request.user,"consumer_profile"):
        return redirect("dashboard")
    
def isConsumer(request):
    if not hasattr(request.user,"consumer_profile"):
        return redirect("dashboard")

@login_required
def consumer_marketplace_view(request):
    isConsumer(request)
    # TODO: Implement marketplace
    return render(request, 'marketplace/consumer_marketplace.html')

@login_required
def business_marketplace_view(request):
    isBusiness(request)
    # TODO: Implement marketplace
    return render(request, 'marketplace/business_marketplace.html')

@login_required
def create_listing_view(request, pk):
    isBusiness(request)

    if request.method == 'POST':
        form = CreateListing(request.POST, request.FILES)

        if form.is_valid():
            listing = form.save(commit=False)
            listing.business = request.user
            listing.save()

            images = request.FILES.getlist('images')
            if len(images) > 5:
                messages.error(request, "You may only upload up to 5 images.")
                return redirect('marketplace:create_listing')
            
            for image in enumerate(images):
                ListingImage.objects.create(
                    listing=listing,
                    image=image
                )

            messages.success(request, 'You have successfully created a listing.')
            return redirect('marketplace:listing_detail', pk=pk)
    else:
        form = CreateListing()

    return render(request, 'marketplace/create_listing.html', {'form': form})

@login_required
def listing_detail_view(request):
    # TODO: implement listing detail view
    return render(request, 'marketplace/listing_detail.html')

@login_required
def respond_to_request_view(request):
    # TODO: implement respond to request
    return render(request, 'marketplace/business_response.html')
