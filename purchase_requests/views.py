from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from .models import PurchaseRequest, Participation, Offer
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages


@login_required
def search_browse_view(request):
    # TODO: Render search form
    return render(request, 'purchase_requests/search_browse.html')


@login_required
def available_list_view(request):
    # TODO: Filter and paginate purchase requests
    return render(request, 'purchase_requests/available_list.html')


@login_required
def purchase_request_detail_view(request, pk):
    pr = get_object_or_404(PurchaseRequest, pk=pk)

    business = getattr(request.user, "businessprofile", None)

    already_joined = False
    if business:
        already_joined = Participation.objects.filter(
            purchase_request=pr,
            business=business
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

    business = getattr(request.user, "businessprofile", None)
    if business:
        Participation.objects.get_or_create(
            business=business,
            purchase_request=pr
        )

    return redirect("purchase_requests:detail", pk=pk)



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
    # TODO: Show buyer's created purchase requests
    return render(request, 'purchase_requests/my_requests.html')


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
