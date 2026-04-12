# admin.py
from django.contrib import admin
from .models import (
    Listing, ListingImage,
    ConsumerRequest, RequestImage,
    BusinessResponse
)

class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'business',
        'category',
        'min_price',
        'max_price',
        'delivery_option',
        'availability',
        'created_at'
    )

    list_filter = (
        'category',
        'delivery_option',
        'availability',
        'created_at'
    )

    search_fields = (
        'title',
        'description',
        'business__username'
    )

    ordering = ('-created_at',)

    inlines = [ListingImageInline]


class RequestImageInline(admin.TabularInline):
    model = RequestImage
    extra = 1


@admin.register(ConsumerRequest)
class ConsumerRequestAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'min_budget',
        'max_budget',
        'delivery_area',
        'needed_by',
        'created_at'
    )

    list_filter = (
        'category',
        'delivery_area',
        'created_at'
    )

    search_fields = (
        'title',
        'description'
    )

    ordering = ('-created_at',)

    inlines = [RequestImageInline]


@admin.register(BusinessResponse)
class BusinessResponseAdmin(admin.ModelAdmin):
    list_display = (
        'business',
        'consumer_request',
        'price',
        'earliest_delivery',
        'latest_delivery',
        'created_at'
    )

    list_filter = (
        'created_at',
        'earliest_delivery'
    )

    search_fields = (
        'business__username',
        'consumer_request__title',
        'message'
    )

    ordering = ('-created_at',)


@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ('listing', 'id')


@admin.register(RequestImage)
class RequestImageAdmin(admin.ModelAdmin):
    list_display = ('request', 'id')
