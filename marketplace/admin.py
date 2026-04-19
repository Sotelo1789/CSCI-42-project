from django.contrib import admin
from .models import Listing, ListingImage, ConsumerRequest, ConsumerRequestImage, BusinessResponse, ListingTransaction, ConsumerRequestTransaction, FavoriteListing, Review

# Register your models here.
@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']

@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ['listing__title','order']
    search_fields = ['listing__title']

@admin.register(ConsumerRequest)
class ConsumerRequestAdmin(admin.ModelAdmin):
    list_display = ['title','response_count','created_at']
    search_fields = ['title']

@admin.register(ConsumerRequestImage)
class ConsumerRequestImageAdmin(admin.ModelAdmin):
    list_display = ['consumer_request__title']
    search_fields = ['consumer_request__title']

@admin.register(BusinessResponse)
class BusinessResponseAdmin(admin.ModelAdmin):
    list_display = ['business__username','consumer_request__title']
    search_fields = ['business__username']

@admin.register(ListingTransaction)
class ListingTransactionAdmin(admin.ModelAdmin):
    list_display = ['listing__title','consumer__username']
    search_fields = ['listing__title']

@admin.register(ConsumerRequestTransaction)
class ConsumerRequestTransactionAdmin(admin.ModelAdmin):
    list_display = ['consumer_request__title','business_response__business__username']
    search_fields = ['consumer_request__title']

@admin.register(FavoriteListing)
class FavoriteListingAdmin(admin.ModelAdmin):
    list_display = ['listing__title','consumer__username','added_favorite_date']
    search_fields = ['listing__title']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['transaction','rating']
    search_fields = ['transaction']