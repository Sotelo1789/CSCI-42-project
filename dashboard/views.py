from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_view(request):
    context = {
        'user': request.user,
        'account_type': request.user.account_type,
    }

    if request.user.is_business:
        try:
            from purchase_requests.models import PurchaseRequest, Participation, Offer
            created_requests = PurchaseRequest.objects.filter(buyer=request.user)
            participations   = Participation.objects.filter(seller=request.user)
            submitted_offers = Offer.objects.filter(seller=request.user)

            context.update({
                'open_requests_count':     created_requests.filter(status='open').count(),
                'participations_count':    participations.count(),
                'submitted_offers_count':  submitted_offers.filter(status='submitted').count(),
                'recent_participations':   participations.select_related('purchase_request')[:5],
                'recent_offers':           submitted_offers.select_related('purchase_request')[:5],
            })
        except Exception:
            pass

    return render(request, 'dashboard/dashboard.html', context)
