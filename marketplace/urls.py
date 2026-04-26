from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # Consumer-specific
    path('consumer', views.consumer_marketplace_view, name='consumer_marketplace'),
    path('listings', views.marketplace_listings_view, name='marketplace_listings'),
    path('create/request', views.create_consumer_request_view, name='create_consumer_request'),
    path('listings/set_favorite/<int:pk>', views.set_favorite, name='set_favorite'),
    path('listings/unfavorite/<int:pk>', views.unfavorite, name='unfavorite'),
    path('listing/set_favorite/<int:pk>', views.set_favorite_in_detail, name='set_favorite_in_detail'),
    path('listing/unfavorite/<int:pk>', views.unfavorite_in_detail, name='unfavorite_in_detail'),
    path('listing/download/toc/<int:pk>', views.download_toc, name='download_toc'),
    path('listing/<int:pk>/pay', views.pay_listing_view, name='pay_listing'),
    path('response/<int:pk>/pay', views.pay_response, name='pay_response'),
    path('review/<int:pk>', views.create_review_view, name='create_review'),
    
    # Business-specific
    path('business', views.business_marketplace_view, name='business_marketplace'),
    path('requests', views.marketplace_consumer_requests_view, name='marketplace_requests'),
    path('create/listing', views.create_listing_view, name='create_listing'),
    path('create/response/request/<int:pk>', views.respond_to_request_view, name='respond_to_request'),
    
    # Available for all with different versions
    path('listing/<int:pk>', views.listing_detail_view, name='listing_detail'),
    path('request/<int:pk>', views.consumer_request_detail_view, name='consumer_request_detail'),
    path('transactions', views.my_transactions_view, name='transactions'),
    path('response/<int:pk>', views.business_response_view, name='business_response_detail'),
    path('response/<int:pk>/download/quotation', views.download_quotation, name='download_quotation'),
]
