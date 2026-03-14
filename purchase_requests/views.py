from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.utils import timezone
from django.core.paginator import Paginator
from .models import PurchaseRequest, Participation, Offer
from authentication.models import BusinessProfile
from .forms import CreatePurchaseRequest, SubmitOffer, AmountInPage, UpdatePurchaseRequestDeadline
from datetime import datetime

"""
Checks if user is a consumer. If yes, redirect to dashboard 
(they should not be able to access pages with this function)
"""
def isBusiness(request):
    if hasattr(request.user,"consumer_profile"):
        return redirect("dashboard")

@login_required
def search_browse_view(request):
    # TODO: Render search form
    return render(request, 'purchase_requests/search_browse.html')


@login_required
def available_list_view(request):
    """Verify that user is business"""
    isBusiness(request)

    """Default number of items per page"""
    page_item_count = 15 

    """Get data from page limiter"""
    dictate_form = AmountInPage(request.GET or None) 

    """
    If there is data, either change number of items per page or stick to default if nothing is in
    """
    if dictate_form.is_valid(): 
        page_item_count = dictate_form.cleaned_data['dictate']
        if page_item_count == None:
            page_item_count = 15

    """
    Get available purchase requests not of the user, and split them by the page
    """
    prlist = PurchaseRequest.objects.exclude(buyer=request.user).filter(status="open").order_by("pk")
    """Ensure all purchase requests are truly open (may need better implementation to cover all possible bases, but for now it works)"""
    for pr in prlist:
        if pr.closing_deadline <= timezone.now():
            pr.status = "closed"
            pr.save()
    prlist = PurchaseRequest.objects.exclude(buyer=request.user).filter(status="open").order_by("pk")

    paginator = Paginator(prlist, page_item_count)
    page_number = request.GET.get("page")
    page_prlist = paginator.get_page(page_number)
    """For more accurate grammar later in the template"""
    is_one_per_page = (page_item_count == 1)

    """
    Fill up the context for the template
    """
    ctx = {
        "prlist" : prlist,
        "page_prlist" : page_prlist,
        "dictate_form" : dictate_form,
        "page_item_count" : page_item_count,
        "is_one_per_page" : is_one_per_page
    }

    return render(request, 'purchase_requests/available_list.html', ctx)


@login_required
def purchase_request_detail_view(request, pk):
    # extra TODO in future iteration: Might want to figure out how to not let users see their own purchase requests this way 
    pr = get_object_or_404(PurchaseRequest, pk=pk)

    business = getattr(request.user, "business_profile", None) # Needs underscore to work

    already_joined = False
    if business:
        already_joined = Participation.objects.filter(
            purchase_request=pr,
            seller=business.client # Looks for client, not business_profile
        ).exists()

    is_closed = pr.closing_deadline <= timezone.now()
    return render(request, 'purchase_requests/detail.html', {
        "pr": pr,
        "already_joined":already_joined,
        "is_closed":is_closed,
        })


@login_required
def join_purchase_request(request, pk):
    pr = get_object_or_404(PurchaseRequest, pk=pk)

    business = getattr(request.user, "business_profile", None) # Needs underscore to work
    if business:
        Participation.objects.get_or_create(
            seller=business.client, # Looks for client, not business_profile
            purchase_request=pr
        )

    return redirect("purchase_requests:detail", pk=pk)


@login_required
def review_list_view(request):
    """Verify that user is business"""
    isBusiness(request)

    """Get all available purchase requests that have the user as a potential seller"""
    all_participations = Participation.objects.filter(seller=request.user, purchase_request__status="open").order_by("purchase_request__closing_deadline")
    
    """Ensures that purchase requests will close once they are attempted to be accessed past the deadline"""
    for participation in all_participations:
        if participation.purchase_request.closing_deadline <= timezone.now():
            pr = participation.purchase_request
            pr.status = "closed"
            pr.save()

    """Refresh the list"""
    all_participations = Participation.objects.filter(seller=request.user, purchase_request__status="open").order_by("purchase_request__closing_deadline")
        
    ctx = {
        "all_participations" : all_participations
    }

    return render(request, 'purchase_requests/review_list.html', ctx)


@login_required
def participate_view(request, pk):
    """Verify that user is business"""
    isBusiness(request)

    """Get the selected purchase request"""
    participation = get_object_or_404(Participation, pk=pk)

    """Officially mark business user as a participating seller"""
    if participation.seller == request.user:
        participation.is_participating = True
        participation.save()

    return redirect('purchase_requests:review_list')


@login_required
def remove_from_review_view(request, pk):
    """Verify that user is business"""
    isBusiness(request)
    
    """Obtain the related purchase request"""
    participation = get_object_or_404(Participation, pk=pk)
    pr = participation.purchase_request

    """Verify that business user is a potential seller, and that the purchase request is still open now"""
    if participation.seller == request.user and pr.status == "open":
        """Then delete the connection between the potentially selling business user and the purchase request"""
        participation.delete()

    return redirect('purchase_requests:review_list')


@login_required
def download_rfq_view(request, pk):
    """Get the purchase request, and then download the RFQ file of that purchase request"""
    pr = get_object_or_404(PurchaseRequest, pk=pk)
    return FileResponse(pr.rfq_file.open('rb'), as_attachment=True)


@login_required
def submit_offer_view(request, pk):
    pr = get_object_or_404(PurchaseRequest, pk=pk)
    # TODO: Handle PDF upload and offer creation/replacement
    return render(request, 'purchase_requests/submit_offer.html', {'pr': pr})


@login_required
def my_offers_view(request):

    if not pr.is_open:
        messages.error(request, 'This purchase request is no longer open.')
        return redirect('purchase_requests:detail', pk)

    existing_offer = Offer.objects.filter(
        purchase_request = pr,
        seller = request.user
    ).first()

    if request.method == 'POST':
        form = SubmitOffer(request.POST, request.FILES)

        if form.is_valid():
            offer_file = form.cleaned_data['offer_file']
            if existing_offer:
                existing_offer.offer_file.delete()
                existing_offer.offer_file = offer_file
                existing_offer.submitted_at = timezone.now()
                existing_offer.save()
                messages.success(request, 'Your offer has been resubmitted successfully.')
            else:
                Offer.objects.create(
                    purchase_request = pr,
                    seller = request.user,
                    offer_file = offer_file
                )
                messages.success(request, 'Your offer has been submitted successfully.')
            return redirect('purchase_requests:detail', pk=pk)
    else:
        form = SubmitOffer()

    return render(request, 'purchase_requests/submit_offer.html',
                  {'pr': pr,
                  'form':form,
                  'existing_offer':existing_offer}
                )


@login_required
def my_requests_view(request):
    """Verify that user is business"""
    isBusiness(request)

    """Default number of items per page"""
    page_item_count = 15 

    """Get data from page limiter"""
    dictate_form = AmountInPage(request.GET or None) 

    """
    If there is data for changing items per page, either 
    change number of items per page or stick to default if nothing is in
    """
    if dictate_form.is_valid(): 
        page_item_count = dictate_form.cleaned_data['dictate']
        if page_item_count == None or page_item_count < 1:
            page_item_count = 15

    """
    If Business user has decided to either change the closing deadline
    of one of their purchase requests or cancel one of their purchase 
    requests, then the code below is followed
    """

    if request.method == "POST":
        # print("Post")
        """
        Get which purchase request is being affected, and how it is being changed
        """
        pr = get_object_or_404(PurchaseRequest, pk=request.POST.get("purchase_request"))
        action = request.POST.get("action")
        # print(action)
        if action == "changeDeadline":
            """
            Obtain the old and \'new\' closing deadline for that purchase request
            """
            old_deadline = pr.closing_deadline 
            new_deadline = request.POST.get("closing_deadline")

            """
            Ensure that new_deadline is of the proper format and datetime datatype (retrieving 
            from POST creates a string, which is not as easily comparable to the datetime data 
            type of old_deadline)
            """

            new_deadline = new_deadline[0:10] + " " + new_deadline[11:16] + old_deadline.strftime(":%S%z")
            date_format = "%Y-%m-%d %H:%M:%S%z"
            new_deadline = datetime.strptime(new_deadline, date_format)

            #print(old_deadline)
            #print(new_deadline)
            #print(old_deadline < new_deadline)
            #print(old_deadline >= new_deadline)

            """
            If the new_deadline is later than the old_deadline and that this purchase request
            is still available at this time when changes will happen, the closing deadline of
            this purchase request is extended to the inputed date and time
            """

            if old_deadline < new_deadline and pr.status == "open":
                pr.closing_deadline = new_deadline
                pr.save()
                # print("Change")
                # print(pr.closing_deadline)
            # else:
                # print("Don\'t change")
        elif action == "cancelRequest":
            """
            If the status is still open at the time of changing, set the
            purchase request's status to cancelled
            """

            if pr.status == "open":
                pr.status = "cancelled"
                pr.save()
                # print("Purchase Request Cancelled")

    """
    Line below is important for gathering datetime data for changing
    deadlines of Business user's own available purchase requests 
    """

    deadline_form = UpdatePurchaseRequestDeadline()

    """
    Get available purchase requests not of the user, and split them by the page
    """
    prlist = PurchaseRequest.objects.filter(status="open",buyer=request.user).order_by("pk")
    """Ensure all purchase requests are truly open"""
    for pr in prlist:
        if pr.closing_deadline <= timezone.now():
            pr.status = "closed"
            pr.save()
    prlist = PurchaseRequest.objects.filter(status="open",buyer=request.user).order_by("pk")

    paginator = Paginator(prlist, page_item_count)
    page_number = request.GET.get("page")
    page_prlist = paginator.get_page(page_number)
    """For more accurate grammar later in the template"""
    is_one_per_page = (page_item_count == 1) 

    """
    Fill up the context for the template
    """
    ctx = {
        "prlist" : prlist,
        "page_prlist" : page_prlist,
        "dictate_form" : dictate_form,
        "page_item_count" : page_item_count,
        "is_one_per_page" : is_one_per_page,
        "deadline_form" : deadline_form
    }

    return render(request, 'purchase_requests/my_requests.html', ctx)


@login_required
def create_purchase_request_view(request):
    if request.method == 'POST':
        form = CreatePurchaseRequest(request.POST, request.FILES)

        if form.is_valid():
            pr = form.save(commit=False)
            pr.buyer = request.user
            pr.save()
            messages.success(request, 'Purchase request has been created successfully.')
            return redirect('purchase_requests:my_requests')
    else:
            form = CreatePurchaseRequest()
    return render(request, 'purchase_requests/create.html', {'form':form})


@login_required
def edit_purchase_request_view(request, pk):
    pr = get_object_or_404(PurchaseRequest, pk=pk, buyer=request.user)
    return render(request, 'purchase_requests/edit.html', {'pr': pr})


# Might need to depreciate this one...or recode my_requests_view to accommodate this function
@login_required
def cancel_purchase_request_view(request, pk):
    # TODO: Cancel purchase request
    return redirect('purchase_requests:my_requests')


@login_required
def view_offers_view(request, pk):
    pr = get_object_or_404(PurchaseRequest, pk=pk, buyer=request.user)
    return render(request, 'purchase_requests/view_offers.html', {'pr': pr})


@login_required
def accept_offer_view(request, pk, offer_pk):
    # TODO: Accept offer, update statuses
    return redirect('purchase_requests:view_offers', pk=pk)


@login_required
def reject_offer_view(request, pk, offer_pk):
    # TODO: Reject offer
    return redirect('purchase_requests:view_offers', pk=pk)
