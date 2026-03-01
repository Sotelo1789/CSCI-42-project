from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.core.paginator import Paginator
from .models import PurchaseRequest, Participation, Offer
from authentication.models import BusinessProfile
from .forms import AmountInPage, UpdatePurchaseRequestDeadline
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
    pr = get_object_or_404(PurchaseRequest, pk=pk)
    return render(request, 'purchase_requests/detail.html', {'pr': pr})


@login_required
def join_purchase_request_view(request, pk):
    # TODO: Create Participation record (joined, not yet participating)
    return redirect('purchase_requests:review_list')


@login_required
def review_list_view(request):
    # TODO: Show joined purchase requests
    return render(request, 'purchase_requests/review_list.html')


@login_required
def participate_view(request, pk):
    # TODO: Mark seller as participant
    return redirect('purchase_requests:review_list')


@login_required
def remove_from_review_view(request, pk):
    # TODO: Remove participation record
    return redirect('purchase_requests:review_list')


@login_required
def download_rfq_view(request, pk):
    pr = get_object_or_404(PurchaseRequest, pk=pk)
    # TODO: Serve RFQ file
    return FileResponse(pr.rfq_file.open('rb'), as_attachment=True)


@login_required
def submit_offer_view(request, pk):
    pr = get_object_or_404(PurchaseRequest, pk=pk)
    # TODO: Handle PDF upload and offer creation/replacement
    return render(request, 'purchase_requests/submit_offer.html', {'pr': pr})


@login_required
def my_offers_view(request):
    # TODO: Show seller's submitted offers
    return render(request, 'purchase_requests/my_offers.html')


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

    if request.method == "POST":
        # print("Post")
        pr = get_object_or_404(PurchaseRequest, pk=request.POST.get("purchase_request"))
        action = request.POST.get("action")
        # print(action)
        if action == "changeDeadline":
            old_deadline = pr.closing_deadline 
            new_deadline = request.POST.get("closing_deadline")

            new_deadline = new_deadline[0:10] + " " + new_deadline[11:16] + old_deadline.strftime(":%S%z")
            date_format = "%Y-%m-%d %H:%M:%S%z"
            new_deadline = datetime.strptime(new_deadline, date_format)

            #print(old_deadline)
            #print(new_deadline)
            #print(old_deadline < new_deadline)
            #print(old_deadline >= new_deadline)

            if old_deadline < new_deadline and pr.status == "open":
                pr.closing_deadline = new_deadline
                pr.save()
                # print("Change")
                # print(pr.closing_deadline)
            # else:
                # print("Don\'t change")
        elif action == "cancelRequest":
            if pr.status == "open":
                pr.status = "cancelled"
                pr.save()
                # print("Purchase Request Cancelled")

    deadline_form = UpdatePurchaseRequestDeadline()

    """
    Get available purchase requests not of the user, and split them by the page
    """
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

    # TODO: Show buyer's created purchase requests
    return render(request, 'purchase_requests/my_requests.html', ctx)


@login_required
def create_purchase_request_view(request):
    # TODO: Create new purchase request
    return render(request, 'purchase_requests/create.html')


@login_required
def edit_purchase_request_view(request, pk):
    pr = get_object_or_404(PurchaseRequest, pk=pk, buyer=request.user)
    return render(request, 'purchase_requests/edit.html', {'pr': pr})


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
