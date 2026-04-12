from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from .forms import CreateListing, RequestSearchFilter, RespondToRequest
from .models import Listing, ListingImage, ConsumerRequest


def isBusiness(request):
    if hasattr(request.user,"consumer_profile"):
        return redirect("dashboard")
    
def isConsumer(request):
    if not hasattr(request.user,"consumer_profile"):
        return redirect("dashboard")

@login_required
def marketplace_view(request):
    acc_type = 'business'
    if hasattr(request.user, "consumer_profile"):
        acc_type = 'consumer'

    if acc_type == 'business':
        requests = ConsumerRequest.objects.exclude(status="closed").order_by("pk")

        filter_form = RequestSearchFilter(request.GET or None)
        if filter_form.is_valid():
            kw = filter_form.cleaned_data.get('keyword')
            cat = filter_form.cleaned_data.get('category')
            min = filter_form.cleaned_data.get('min_price')
            max = filter_form.cleaned_data.get('max_price')
            area = filter_form.cleaned_data.get('area')

            if kw:
                from django.db.models import Q
                requests = request.filter(
                    Q(title__icontains=kw) | Q(description__icontains=kw)
                )
            if cat:
                requests = requests.filter(category=cat)
            if min is not None:
                requests = requests.filter(budget__gte=min)
            if max is not None:
                requests = requests.filter(budget__lte=max)
            if area:
                requests = requests.filter(delivery_area__icontains=area)

        paginator = Paginator(requests, 15)
        page_number = request.GET.get("page")
        page_requests = paginator.get_page(page_number)

        ctx = {
            "acc_type": acc_type,
            "requests": requests,
            "page_requests": page_requests,
            "filter_form": filter_form,
            "request_get": "&".join(f"{k}={v}" for k, v in request.GET.items() if k != "page"),
        }
    else:
        null = 1 # placeholder
        # TODO: Implement consumer marketplace

    return render(request, 'marketplace/marketplace.html', ctx)

@login_required
def create_listing_view(request):
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
            return redirect('marketplace:listing_detail', pk=listing.pk)
    else:
        form = CreateListing()

    return render(request, 'marketplace/create_listing.html', {'form': form})

@login_required
def listing_detail_view(request):
    # TODO: implement listing detail view
    return render(request, 'marketplace/listing_detail.html')

@login_required
def respond_to_request_view(request, pk):
    isBusiness(request)
    req = get_object_or_404(ConsumerRequest, id=pk)
    business = request.user

    if request.method == 'POST':
        form = RespondToRequest(request.POST, request.FILES)

        if form.is_valid():
            response = form.save(commit=False)
            response.consumer_request = req
            response.business = business
            response.save()
            req.status = 'response'

            messages.success(request, 'You have successfully submitted a response.')
            return redirect('marketplace:request_detail', pk=pk)
    else:
        form = RespondToRequest()

    return render(request, 'marketplace/business_response.html', {
        'form': form,
        'req': req
    })
