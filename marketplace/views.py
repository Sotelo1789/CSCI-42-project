from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CreateListing, RespondToRequest
from .models import Listing, ListingImage


@login_required
def marketplace_view(request):
    # TODO: Implement marketplace
    return render(request, 'marketplace/marketplace.html')

def create_listing_view(request):
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
            return redirect('marketplace:my_listings')
    else:
        form = CreateListing()

    return render(request, 'marketplace/create_listing.html', {'form': form})

def respond_to_request_view(request):
    return render(request, 'marketplace/business_response.html')
