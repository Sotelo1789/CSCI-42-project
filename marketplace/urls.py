from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # Consumer-specific
    path('consumer', views.consumer_marketplace_view, name='consumer_marketplace'), #DONE
    path('listings', views.marketplace_listings_view, name='marketplace_listings'), #DONE
    path('create/request', views.create_consumer_request_view, name='create_consumer_request'),
    path('listing/set_favorite/<int:pk>', views.set_favorite, name='set_favorite'), #DONE
    path('listing/unfavorite/<int:pk>', views.unfavorite, name='unfavorite'), #DONE
    # TODO path('consumer/my-requests', views.my_consumer_requests_view, name='my_consumer_requests'),

    # Business-specific
    path('business', views.business_marketplace_view, name='business_marketplace'),
    path('requests', views.marketplace_consumer_requests_view, name='marketplace_requests'),
    path('create/listing', views.create_listing_view, name='create_listing'), #DONE
    # TODO path('create/response/request/<int:pk>', views.respond_to_request_view, name='respond_to_request'),
    # TODO path('business/my-listings/', views.my_marketplace_listings_view, name='my_listings'),
    # TODO path('business/my-responses/', views.my_business_responses_view, name='my_responses'),

    # Available for all with different versions
    path('listing/<int:pk>', views.listing_detail_view, name='listing_detail'),
    # TODO path('request/<int:pk>', views.request_detail_view, name='request_detail')
    
]
