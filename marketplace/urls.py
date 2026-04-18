from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # Consumer-specific
    path('consumer', views.consumer_marketplace_view, name='consumer_marketplace'), #DONE
    path('listings', views.marketplace_listings_view, name='marketplace_listings'), #DONE
    path('create/request', views.create_consumer_request_view, name='create_consumer_request'), #DONE
    path('listings/set_favorite/<int:pk>', views.set_favorite, name='set_favorite'), #DONE
    path('listings/unfavorite/<int:pk>', views.unfavorite, name='unfavorite'), #DONE
    path('listing/set_favorite/<int:pk>', views.set_favorite_in_detail, name='set_favorite_in_detail'), #DONE
    path('listing/unfavorite/<int:pk>', views.unfavorite_in_detail, name='unfavorite_in_detail'), #DONE
    path('listing/download/toc/<int:pk>', views.download_toc, name='download_toc'), #DONE
    # TODO path('consumer/my-requests', views.my_consumer_requests_view, name='my_consumer_requests'),
    # potential TODO path('listings/my-favorites', views.my_favorite_listings_view, name='my_favorite_listings'),
    # potential TODO path('request/<int:pk>/edit', views.edit_consumer_request_view, name='edit_consumer_request'),
    path('listing/<int:pk>/pay', views.pay_listing_view, name='pay_listing'), #DONE
    path('response/<int:pk>/pay', views.pay_response, name='pay_response'), #DONE
    # potential TODO path('listing/<int:pk>/review', views.review_listing_view, name='review_listing'),
    # potential TODO path('response/<int:pk>/review', views.review_response_view, name='review_response'),

    # Business-specific
    path('business', views.business_marketplace_view, name='business_marketplace'), #DONE
    path('requests', views.marketplace_consumer_requests_view, name='marketplace_requests'), #DONE
    path('create/listing', views.create_listing_view, name='create_listing'), #DONE
    path('create/response/request/<int:pk>', views.respond_to_request_view, name='respond_to_request'), #DONE
    # potential TODO path('listing/<int:pk>/edit', views.edit_listing_view, name='edit_listing'),
    # potential TODO path('response/<int:pk>/edit', views.edit_response_view, name='edit_response'),
    # potential TODO path('business/my-listings/', views.my_marketplace_listings_view, name='my_listings'),
    # potential TODO path('business/my-responses/', views.my_business_responses_view, name='my_responses'),
    # potential TODO path('business/reviews/', views.business_reviews_view, name='business_reviews'),

    # Available for all with different versions
    path('listing/<int:pk>', views.listing_detail_view, name='listing_detail'), #DONE
    path('request/<int:pk>', views.consumer_request_detail_view, name='consumer_request_detail'), #DONE for this iter3
    path('transactions', views.my_transactions_view, name='transactions'), #DONE
    path('response/<int:pk>', views.business_response_view, name='business_response_detail'), #DONE
    path('response/<int:pk>/download/quotation', views.download_quotation, name='download_quotation'), #DONE
    # potential TODO path('chat/listing/<int:pk>', views.chat_over_listing_view, name='chat_over_listing),
    # potential TODO path('chat/response/<int:pk>', views.chat_over_response_view, name='chat_over_response),
]
