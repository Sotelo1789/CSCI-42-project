from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.marketplace_view, name='marketplace'),
    path('listings/create/', views.create_listing_view, name='create_listing'),
    path('listings/<int:pk>/', views.listing_detail_view, name='listing_detail'),
    path('requests/<int:pk>/respond', views.respond_to_request_view, name='business_response'),
]
