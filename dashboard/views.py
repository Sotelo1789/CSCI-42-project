from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_view(request):
    # TODO: Aggregate metrics for business or consumer dashboard
    return render(request, 'dashboard/dashboard.html')
