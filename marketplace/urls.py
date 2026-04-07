from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.marketplace_view, name='marketplace'),
    path('listing/create/', views.create_listing_view, name='create_listing'),
]
