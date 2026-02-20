from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls', namespace='authentication')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('purchase-requests/', include('purchase_requests.urls', namespace='purchase_requests')),
    path('marketplace/', include('marketplace.urls', namespace='marketplace')),
    path('profile/', include('profiles.urls', namespace='profiles')),
    # Root redirects to login
    path('', RedirectView.as_view(url='/auth/login/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
