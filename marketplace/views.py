from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import FileResponse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import CreateListing, CreateConsumerRequest, RespondToRequest, RespondToRequest, ListingSearchFilterForm, RequestSearchFilterForm, AmountInPage, CreateListingTransaction, ChooseTransactionKind, ReviewForm
from .models import Listing, ListingImage, ConsumerRequest, ConsumerRequestImage, BusinessResponse, FavoriteListing, Transaction, ListingTransaction, ConsumerRequestTransaction, Review
from authentication.models import BusinessProfile

"""
Shows consumer marketplace
"""
@login_required
def consumer_marketplace_view(request):
    if not hasattr(request.user,"consumer_profile"):
        return redirect('dashboard:dashboard')

    return render(request, 'marketplace/consumer_marketplace.html')

"""
Shows all available marketplace listings
"""
@login_required
def marketplace_listings_view(request):
    if not hasattr(request.user,"consumer_profile"):
        return redirect('dashboard:dashboard')

    page_item_count = 15
    dictate_form = AmountInPage(request.GET or None)
    if dictate_form.is_valid():
        page_item_count = dictate_form.cleaned_data['dictate'] or 15

    listings = Listing.objects.filter(business__business_profile__status='approved').order_by('-updated_at')
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

    paginatorl = Paginator(listings, page_item_count)
    page_number = request.GET.get("page")
    page_listings = paginatorl.get_page(page_number)
    is_one_per_page = (page_item_count == 1)

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

"""
Shows business marketplace
"""
@login_required
def business_marketplace_view(request):
    if not hasattr(request.user,"business_profile"):
        return redirect('dashboard:dashboard')
    return render(request, 'marketplace/business_marketplace.html')

"""
Shows all available marketplace consumer requests
"""
@login_required
def marketplace_consumer_requests_view(request):
    if not hasattr(request.user,"business_profile"):
        return redirect('dashboard:dashboard')

    page_item_count = 15
    dictate_form = AmountInPage(request.GET or None)
    if dictate_form.is_valid():
        page_item_count = dictate_form.cleaned_data['dictate'] or 15

    crs = ConsumerRequest.objects.filter(status='open').order_by('-updated_at')

    filter_form = RequestSearchFilterForm(request.GET or None)
    if filter_form.is_valid():
        kw = filter_form.cleaned_data.get('keyword')
        cat = filter_form.cleaned_data.get('category')
        bmin = filter_form.cleaned_data.get('min_price')
        bmax = filter_form.cleaned_data.get('max_price')
        area = filter_form.cleaned_data.get('delivery_area')

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
        if area:
            crs = crs.filter(delivery_area__icontains=area)

    paginator = Paginator(crs, page_item_count)
    page_number = request.GET.get("page")
    page_consumer_requests = paginator.get_page(page_number)
    is_one_per_page = (page_item_count == 1)

    page_respondedrequests = [False]*page_consumer_requests.object_list.count()

    request_order = 0
    for consumer_request in page_consumer_requests.object_list:
        has_responded = False
        responses = BusinessResponse.objects.filter(consumer_request=consumer_request)
        for response in responses:
            if response.business == request.user:
                has_responded = True
        page_respondedrequests[request_order] = (has_responded,consumer_request.pk)
        request_order += 1

    ctx = {
        "crs": crs,
        "page_consumer_requests": page_consumer_requests,
        "page_respondedrequests": page_respondedrequests,
        "dictate_form": dictate_form,
        "filter_form": filter_form,
        "page_item_count": page_item_count,
        "is_one_per_page": is_one_per_page,
        "request_get": "&".join(f"{k}={v}" for k, v in request.GET.items() if k != "page"),
    }

    return render(request, 'marketplace/marketplace_requests.html', ctx)

"""
Allows marketplace listing creation
"""
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

"""
Shows details of marketplace listing
"""
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

"""
Allows business response creation for marketplace consumer request
"""
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
            
            min_price = cr.min_price
            max_price = cr.max_price

            if(min_price > br.price or max_price < br.price):
                messages.error(request, 'Price is not within given range')
                return redirect('marketplace:respond_to_request', pk=pk)
            
            br.save()

            cr.response_count = cr.response_count + 1
            cr.save()

            messages.success(request, 'You have successfully created a business response.')
            return redirect('marketplace:consumer_request_detail', pk=cr.pk)
    else:
        form = RespondToRequest()

    return render(request, 'marketplace/respond_to_request.html', {'form': form, 'cr': cr})

"""
Shows business response for a marketplace consumer request
"""
@login_required
def business_response_view(request, pk):
    br = get_object_or_404(BusinessResponse, pk=pk)

    if hasattr(request.user, "business_profile"):
        if br.business != request.user:
            return redirect('dashboard:dashboard')
    elif hasattr(request.user, "consumer_profile"):
        if br.consumer_request.consumer != request.user:
            return redirect('dashboard:dashboard')

    is_accepted = ConsumerRequestTransaction.objects.filter(consumer_request=br.consumer_request, business_response=br).exists()
    is_reviewed = Review.objects.filter(transaction__consumerrequesttransaction__business_response=br).exists()
    
    ctx = {
        'br': br,
        'is_accepted': is_accepted,
        'is_reviewed': is_reviewed
    }

    return render(request, 'marketplace/business_response_detail.html', ctx)

"""
Allows creation of marketplace consumer request
"""
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

            messages.success(request, 'You have successfully created a consumer request.')
            return redirect('marketplace:consumer_request_detail', pk=cr.pk)
    else:
        form = CreateConsumerRequest()

    return render(request, 'marketplace/create_consumer_request.html', {'form': form})

"""
Shows details of marketplace consumer request
"""
@login_required
def consumer_request_detail_view(request, pk):
    cr = get_object_or_404(ConsumerRequest, pk=pk)
    try:
        crt = ConsumerRequestTransaction.objects.get(consumer_request=cr)
    except:
        crt = None

    if hasattr(request.user, "consumer_profile"):
        if cr.consumer != request.user:
            return redirect('dashboard:dashboard')
    elif hasattr(request.user, "business_profile"):
        if cr.status != "open" and not (crt and crt.business_response.business == request.user):
            return redirect('dashboard:dashboard')

    has_responded = BusinessResponse.objects.filter(consumer_request=cr, business=request.user).exists()
    if has_responded:
        br = BusinessResponse.objects.get(consumer_request=cr, business=request.user)
    else:
        br = None

    has_chosen = ConsumerRequestTransaction.objects.filter(consumer_request=cr).exists()

    if has_chosen:
        crt = ConsumerRequestTransaction.objects.filter(consumer_request=cr)
    else:
        crt = None

    has_chosen_you = ConsumerRequestTransaction.objects.filter(consumer_request=cr, business_response__business=request.user).exists()

    ctx = {
        'cr': cr,
        'br': br,
        'crt': crt,
        'has_responded': has_responded,
        'has_chosen_you': has_chosen_you
    }

    return render(request, 'marketplace/consumer_request_detail.html', ctx)

"""
Allows downloading of terms and conditions file
"""
@login_required
def download_toc(request, pk):
    if not hasattr(request.user,"consumer_profile"):
        return redirect('dashboard:dashboard')
    """Get the listing, and then download the TOC file of that listing"""
    listing = get_object_or_404(Listing, pk=pk)
    return FileResponse(listing.terms_conditions.open('rb'), as_attachment=True)

"""
Allows downloading of quotation file
"""
@login_required
def download_quotation(request, pk):
    """Get the business response, and then download the quotation file of that business response"""
    br = get_object_or_404(BusinessResponse, pk=pk)
    return FileResponse(br.quotation.open('rb'), as_attachment=True)

"""
Allows setting of listing as favorite
"""
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

"""
Allows setting of listing as not favorite
"""
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

"""
Allows setting of listing as favorite in listing detail view
"""
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

"""
Allows setting of listing as not favorite in listing detail view
"""
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

"""
Allows paying over a listing
"""
@login_required
def pay_listing_view(request, pk):
    if not hasattr(request.user,"consumer_profile"):
        return redirect('dashboard:dashboard')

    listing = get_object_or_404(Listing,pk=pk)

    if listing.availability == False:
        return redirect('marketplace:listing_detail', pk=pk)

    if request.method == 'POST':
        pay_form = CreateListingTransaction(request.POST)

        if pay_form.is_valid():
            lt = pay_form.save(commit=False)
            lt.consumer = request.user
            lt.listing = listing
            lt.transaction_type = "L"

            min_price = listing.min_price
            max_price = listing.max_price

            if(min_price > lt.price or max_price < lt.price):
                messages.error(request, 'Price is not within given range')
                return redirect('marketplace:pay_listing', pk=pk)
            
            lt.save()

            messages.success(request, 'You have successfully bought something. For smoother proceedings, have the decided amount ready to give to the business')
            return redirect('marketplace:listing_detail', pk=pk)
    else:
        pay_form = CreateListingTransaction()

    ctx = {
        'listing': listing,
        'pay_form': pay_form
    }

    return render(request, 'marketplace/pay_listing.html', ctx)

"""
Allows paying over a consumer request
"""
@login_required
def pay_response(request, pk):
    if not hasattr(request.user,"consumer_profile"):
        return redirect('dashboard:dashboard')

    business_response = get_object_or_404(BusinessResponse,pk=pk)

    if business_response.consumer_request.needed_by <= timezone.now():
        return redirect('marketplace:business_response_detail', pk=pk)

    ConsumerRequestTransaction.objects.create(
        business_response=business_response,
        consumer_request=business_response.consumer_request,
        price=business_response.price,
        transaction_type="C"
    )

    consumer_request = business_response.consumer_request
    consumer_request.status = 'closed'
    consumer_request.save()

    messages.success(request, 'You have successfully bought something. For smoother proceedings, have the decided amount ready to give to the business')
    return redirect('marketplace:business_response_detail', pk=pk)

"""
Shows all available transactions of user
"""
@login_required
def my_transactions_view(request):
    if hasattr(request.user,"consumer_profile"):
        tk = "listing"
        transactions = ListingTransaction.objects.filter(consumer=request.user).order_by("-created_at")
    elif hasattr(request.user,"business_profile"):
        tk = "consumer_request"
        transactions = ConsumerRequestTransaction.objects.filter(business_response__business=request.user).order_by("-created_at")

    page_item_count = 15
    dictate_form = AmountInPage(request.GET or None)
    if dictate_form.is_valid():
        page_item_count = dictate_form.cleaned_data['dictate'] or 15

    filter_form = ChooseTransactionKind(request.GET or None)
    if filter_form.is_valid():
        tk = filter_form.cleaned_data.get('transaction') or tk
        if hasattr(request.user,"consumer_profile"):
            if tk == 'listing':
                transactions = ListingTransaction.objects.filter(consumer=request.user)
            elif tk == 'consumer_request':
                transactions = ConsumerRequestTransaction.objects.filter(consumer_request__consumer=request.user)
        elif hasattr(request.user,"business_profile"):
            if tk == 'listing':
                transactions = ListingTransaction.objects.filter(listing__business=request.user)
            elif tk == 'consumer_request':
                transactions = ConsumerRequestTransaction.objects.filter(business_response__business=request.user)

        kw = filter_form.cleaned_data.get('keyword')
        cat = filter_form.cleaned_data.get('category')
        min_price = filter_form.cleaned_data.get('min_price')
        max_price = filter_form.cleaned_data.get('max_price')
        person = filter_form.cleaned_data.get('person')
        edate = filter_form.cleaned_data.get('earliest_date')
        ldate = filter_form.cleaned_data.get('latest_date')

        if kw:
            if tk == 'listing':
                transactions = transactions.filter(listing__title__icontains=kw)
            if tk == 'consumer_request':
                transactions = transactions.filter(consumer_request__title__icontains=kw)
        if cat:
            if tk == 'listing':
                transactions = transactions.filter(listing__category=cat)
            if tk == 'consumer_request':
                transactions = transactions.filter(consumer_request__category=cat)
        if min_price is not None:
            transactions = transactions.filter(price__gte=min_price)
        if max_price is not None:
            transactions = transactions.filter(price__lte=max_price)
        if person:
            if tk == 'listing':
                transactions = transactions.filter(listing__business__business_profile__business_name__icontains=person)
            if tk == 'consumer_request':
                transactions = transactions.filter(business_response__business__business_profile__business_name__icontains=person)
        if edate is not None:
            transactions = transactions.filter(created_at__gte=edate)
        if ldate is not None:
            transactions = transactions.filter(created_at__lte=ldate)

    paginator = Paginator(transactions, page_item_count)
    page_number = request.GET.get("page")
    page_transactions = paginator.get_page(page_number)
    is_one_per_page = (page_item_count == 1)

    ctx = {
        'transactions': transactions,
        'page_transactions': page_transactions,
        'tk': tk,
        'dictate_form': dictate_form,
        'filter_form': filter_form,
        'page_item_count': page_item_count,
        'is_one_per_page': is_one_per_page,
        "request_get": "&".join(f"{k}={v}" for k, v in request.GET.items() if k != "page")
    }
    return render(request, 'marketplace/marketplace_transactions.html', ctx)

"""
Allows creation of review over a transaction
"""
@login_required
def create_review_view(request, pk):
    if not hasattr(request.user,"consumer_profile"):
        return redirect('dashboard:dashboard')

    transaction = get_object_or_404(Transaction, pk=pk)
    if transaction.transaction_type == "C":
        transaction = transaction.consumerrequesttransaction
        if transaction.consumer_request.consumer != request.user:
            return redirect('dashboard:dashboard')
    else:
        transaction = transaction.listingtransaction
        if transaction.consumer != request.user:
            return redirect('dashboard:dashboard')

    if request.method == "POST":
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.transaction = transaction
            review.save()

            if transaction.transaction_type == "C":
                business = transaction.business_response.business.business_profile
            elif transaction.transaction_type == "L":
                business = transaction.listing.business.business_profile
            business.update_rate()

            messages.success(request, 'Review created')
            if transaction.transaction_type == "C":
                return redirect('marketplace:consumer_request_detail', pk=transaction.consumer_request.pk)
            elif transaction.transaction_type == "L":
                return redirect('marketplace:listing_detail', pk=transaction.listing.pk)

    else:
        form = ReviewForm()

    ctx = {
        'transaction': transaction,
        'form': form
    }

    return render(request, "marketplace/make_review.html", ctx)
