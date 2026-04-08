from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('consumer', views.consumer_marketplace_view, name='consumer_marketplace'),
    path('business', views.business_marketplace_view, name='business_marketplace'),
    path('listings/create/', views.create_listing_view, name='create_listing'),
    path('listings/<int:pk>/', views.listing_detail_view, name='listing_detail'),
]
