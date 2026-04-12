from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import FileResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import CreateListing, CreateConsumerRequest, RespondToRequest, RespondToRequest, ListingSearchFilterForm, RequestSearchFilterForm, AmountInPage
from .models import Listing, ListingImage, ConsumerRequest, ConsumerRequestImage, BusinessResponse, FavoriteListing
from authentication.models import BusinessProfile

@login_required
def consumer_marketplace_view(request):
    if not hasattr(request.user,"consumer_profile"):
        return redirect('dashboard:dashboard')

    return render(request, 'marketplace/consumer_marketplace.html')

@login_required
def marketplace_listings_view(request):
    if not hasattr(request.user,"consumer_profile"):
        return redirect('dashboard:dashboard')

    page_item_count = 15
    dictate_form = AmountInPage(request.GET or None)
    if dictate_form.is_valid():
        page_item_count = dictate_form.cleaned_data['dictate'] or 15

    listings = Listing.objects.filter(business__business_profile__status='approved')
    businesses = BusinessProfile.objects.all()

    for business in businesses:
        business.update_rate()

    filter_form = ListingSearchFilterForm(request.GET or None)
    if filter_form.is_valid():
        kw = filter_form.cleaned_data.get('keyword')
        cat = filter_form.cleaned_data.get('category')
        bmin = filter_form.cleaned_data.get('min_price')
        bmax = filter_form.cleaned_data.get('max_price')
        area = filter_form.cleaned_data.get('area')
        rate = filter_form.cleaned_data.get('rating')
        avail = filter_form.cleaned_data.get('availability')

        if kw:
            from django.db.models import Q
            listings = listings.filter(
                Q(title__icontains=kw) | Q(description__icontains=kw)
            )
        if cat:
            listings = listings.filter(category=cat)
        if bmin is not None:
            listings = listings.filter(min_price__gte=bmin)
        if bmax is not None:
            listings = listings.filter(max_price__lte=bmax)
        if area:
            listings = listings.filter(delivery_area__icontains=area)
        if rate is not None:
            listings = listings.filter(business__business_profile__rating__gte=rate)
        if avail is not None:
            if avail == 'true':
                listings = listings.filter(availability=True)
            elif avail == 'false':
                listings = listings.filter(availability=False)

    print(listings)
    
    paginatorl = Paginator(listings, page_item_count)
    page_number = request.GET.get("page")
    page_listings = paginatorl.get_page(page_number)
    is_one_per_page = (page_item_count == 1)

    print(page_listings.object_list.count())

    page_favedlistings = [False]*page_listings.object_list.count()

    list_order = 0
    for listing in page_listings.object_list:
        is_favorite = False
        favlists = FavoriteListing.objects.filter(listing=listing)
        for favlist in favlists:
            if favlist.consumer == request.user:
                is_favorite = True
        page_favedlistings[list_order] = (is_favorite,listing.pk)
        list_order += 1

    print(page_favedlistings)
    
    ctx = {
        "listings": listings,
        "page_listings": page_listings,
        "page_favedlistings": page_favedlistings,
        "dictate_form": dictate_form,
        "filter_form": filter_form,
        "page_item_count": page_item_count,
        "is_one_per_page": is_one_per_page,
        "request_get": "&".join(f"{k}={v}" for k, v in request.GET.items() if k != "page"),
    }

    return render(request, 'marketplace/marketplace_listings.html', ctx)

@login_required
def business_marketplace_view(request):
    if not hasattr(request.user,"business_profile"):
        return redirect('dashboard:dashboard')
    # TODO: Implement marketplace
    return render(request, 'marketplace/business_marketplace.html')

@login_required
def marketplace_consumer_requests_view(request):
    if not hasattr(request.user,"business_profile"):
        return redirect('dashboard:dashboard')
    
    page_item_count = 15
    dictate_form = AmountInPage(request.GET or None)
    if dictate_form.is_valid():
        page_item_count = dictate_form.cleaned_data['dictate'] or 15

    crs = ConsumerRequest.objects.filter(status='open')
    
    filter_form = RequestSearchFilterForm(request.GET or None)
    if filter_form.is_valid():
        kw = filter_form.cleaned_data.get('keyword')
        cat = filter_form.cleaned_data.get('category')
        bmin = filter_form.cleaned_data.get('min_price')
        bmax = filter_form.cleaned_data.get('max_price')
        
        if kw:
            from django.db.models import Q
            crs = crs.filter(
                Q(title__icontains=kw) | Q(description__icontains=kw)
            )
        if cat:
            crs = crs.filter(category=cat)
        if bmin is not None:
            crs = crs.filter(min_price__gte=bmin)
        if bmax is not None:
            crs = crs.filter(max_price__lte=bmax)
        
    paginator = Paginator(crs, page_item_count)
    page_number = request.GET.get("page")
    page_consumer_requests = paginator.get_page(page_number)
    is_one_per_page = (page_item_count == 1)

    ctx = {
        "crs": crs,
        "page_consumer_requests": page_consumer_requests,
        "dictate_form": dictate_form,
        "filter_form": filter_form,
        "page_item_count": page_item_count,
        "is_one_per_page": is_one_per_page,
        "request_get": "&".join(f"{k}={v}" for k, v in request.GET.items() if k != "page"),
    }
    
    return render(request, 'marketplace/marketplace_requests.html', ctx)

@login_required
def create_listing_view(request):
    if not hasattr(request.user,"business_profile"):
        return redirect('dashboard:dashboard')

    if request.method == 'POST':
        form = CreateListing(request.POST, request.FILES)

        if form.is_valid():
            images = request.FILES.getlist('images')
            if len(images) > 5:
                messages.error(request, "You may only upload up to 5 images.")
                return redirect('marketplace:create_listing')

            listing = form.save(commit=False)
            listing.business = request.user
            listing.save()
            
            is_primary = True
            listimages = [None]*5
            
            for order, image in enumerate(images, start=0):
                listimages[order] = ListingImage.objects.create(
                    listing=listing,
                    image=image,
                    order=order,
                    is_primary=is_primary
                )
                is_primary = False

            messages.success(request, 'You have successfully created a listing.')
            return redirect('marketplace:listing_detail', pk=listing.pk)
    else:
        form = CreateListing()

    return render(request, 'marketplace/create_listing.html', {'form': form})

@login_required
def listing_detail_view(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    if hasattr(request.user, "business_profile"):
        if listing.business != request.user:
            return redirect('dashboard:dashboard')
    elif hasattr(request.user, "consumer_profile"):
        if listing.business.business_profile.status != "approved":
            return redirect('dashboard:dashboard')
        listing.view_count = listing.view_count + 1
        listing.save()

    is_favorite = FavoriteListing.objects.filter(listing=listing, consumer=request.user).exists()
    ctx = {
        'listing': listing,
        'is_favorite': is_favorite
    }

    return render(request, 'marketplace/listing_detail.html', ctx)

@login_required
def respond_to_request_view(request, pk):
    if not hasattr(request.user,"business_profile"):
        return redirect('dashboard:dashboard')
    
    cr = get_object_or_404(ConsumerRequest, pk=pk)
    if cr.status != "open": 
        messages.error(request, "That Consumer Request is no longer open")
        return redirect('dashboard:dashboard')

    if request.method == 'POST':
        form = RespondToRequest(request.POST, request.FILES)

        if form.is_valid():
            
            br = form.save(commit=False)
            br.business = request.user
            br.consumer_request = cr
            br.save()

            cr.response_count = cr.response_count + 1
            cr.save()
            
            messages.success(request, 'You have successfully created a business response.')
            return redirect('marketplace:consumer_request_detail', pk=cr.pk)
    else:
        form = RespondToRequest()
    
    # TODO: implement business response creation
    return render(request, 'marketplace/respond_to_request.html', {'form': form, 'cr': cr})

@login_required
def create_consumer_request_view(request):
    if not hasattr(request.user,"consumer_profile"):
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = CreateConsumerRequest(request.POST, request.FILES)

        if form.is_valid():
            images = request.FILES.getlist('images')
            if len(images) > 5:
                messages.error(request, "You may only upload up to 5 images.")
                return redirect('marketplace:create_consumer_request')
            
            cr = form.save(commit=False)
            cr.consumer = request.user
            cr.save()
            
            crimages = [None]*5
            
            for order, image in enumerate(images, start=0):
                crimages[order] = ConsumerRequestImage.objects.create(
                    consumer_request=cr,
                    image=image,
                )

            messages.success(request, 'You have successfully created a consumer_request.')
            return redirect('marketplace:consumer_request_detail', pk=cr.pk)
    else:
        form = CreateConsumerRequest()
    
    # TODO: implement consumer request creation
    return render(request, 'marketplace/create_consumer_request.html', {'form': form})

@login_required
def consumer_request_detail_view(request, pk):
    cr = get_object_or_404(ConsumerRequest, pk=pk)

    if hasattr(request.user, "consumer_profile"):
        if cr.consumer != request.user:
            return redirect('dashboard:dashboard')
    elif hasattr(request.user, "business_profile"):
        if cr.status != "open":
            return redirect('dashboard:dashboard')

    has_responded = BusinessResponse.objects.filter(consumer_request=cr, business=request.user).exists()
    ctx = {
        'cr': cr,
        'has_responded': has_responded
    }

    return render(request, 'marketplace/consumer_request_detail.html', ctx)

@login_required
def download_toc(request, pk):
    if not hasattr(request.user,"consumer_profile"):
        return redirect('dashboard:dashboard')
    """Get the listing, and then download the TOC file of that listing"""
    listing = get_object_or_404(Listing, pk=pk)
    return FileResponse(listing.terms_conditions.open('rb'), as_attachment=True)

@login_required
def set_favorite(request, pk):
    if not hasattr(request.user,"consumer_profile"):
        return redirect('dashboard:dashboard')
    consumer = request.user
    listing = get_object_or_404(Listing, pk=pk)
    favlisting_exists = FavoriteListing.objects.filter(consumer=consumer, listing=listing).exists()

    if not favlisting_exists:
        FavoriteListing.objects.get_or_create(
            consumer=consumer,
            listing=listing,
        )
    
    return redirect('marketplace:marketplace_listings')

@login_required
def unfavorite(request, pk):
    if not hasattr(request.user,"consumer_profile"):
        return redirect('dashboard:dashboard')
    consumer = request.user
    listing = get_object_or_404(Listing, pk=pk)
    favlisting = FavoriteListing.objects.filter(consumer=consumer, listing=listing)

    if favlisting.exists():
        favlisting.delete()
    
    return redirect('marketplace:marketplace_listings')

@login_required
def set_favorite_in_detail(request, pk):
    if not hasattr(request.user,"consumer_profile"):
        return redirect('dashboard:dashboard')
    consumer = request.user
    listing = get_object_or_404(Listing, pk=pk)
    favlisting_exists = FavoriteListing.objects.filter(consumer=consumer, listing=listing).exists()

    if not favlisting_exists:
        FavoriteListing.objects.get_or_create(
            consumer=consumer,
            listing=listing,
        )
    
    return redirect('marketplace:listing_detail',pk=pk)

@login_required
def unfavorite_in_detail(request, pk):
    if not hasattr(request.user,"consumer_profile"):
        return redirect('dashboard:dashboard')
    consumer = request.user
    listing = get_object_or_404(Listing, pk=pk)
    favlisting = FavoriteListing.objects.filter(consumer=consumer, listing=listing)

    if favlisting.exists():
        favlisting.delete()
    
    return redirect('marketplace:listing_detail',pk=pk)