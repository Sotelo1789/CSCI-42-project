from django.urls import path
from . import views

app_name = 'purchase_requests'

urlpatterns = [
    # Browse / search
    path('', views.search_browse_view, name='search_browse'),
    path('available/', views.available_list_view, name='available_list'),
    path('<int:pk>/', views.purchase_request_detail_view, name='detail'),
    path('<int:pk>/join/', views.join_purchase_request_view, name='join'),

    # Review list
    path('review/', views.review_list_view, name='review_list'),
    path('<int:pk>/participate/', views.participate_view, name='participate'),
    path('<int:pk>/remove/', views.remove_from_review_view, name='remove'),
    path('<int:pk>/download-rfq/', views.download_rfq_view, name='download_rfq'),

    # Offers
    path('<int:pk>/submit-offer/', views.submit_offer_view, name='submit_offer'),
    path('my-offers/', views.my_offers_view, name='my_offers'),

    # My purchase requests (as buyer)
    path('my-requests/', views.my_requests_view, name='my_requests'),
    path('my-requests/create/', views.create_purchase_request_view, name='create'),
    path('my-requests/<int:pk>/edit/', views.edit_purchase_request_view, name='edit'),
    path('my-requests/<int:pk>/cancel/', views.cancel_purchase_request_view, name='cancel'),
    path('my-requests/<int:pk>/offers/', views.view_offers_view, name='view_offers'),
    path('my-requests/<int:pk>/offers/<int:offer_pk>/accept/', views.accept_offer_view, name='accept_offer'),
    path('my-requests/<int:pk>/offers/<int:offer_pk>/reject/', views.reject_offer_view, name='reject_offer'),
]
