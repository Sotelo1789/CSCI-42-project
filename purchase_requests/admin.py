from django.contrib import admin
from .models import PurchaseRequest, Participation, Offer


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'buyer', 'status', 'category', 'budget', 'closing_deadline', 'created_at']
    list_filter = ['status', 'category']
    search_fields = ['title', 'buyer__username']


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ['seller', 'purchase_request', 'joined_at', 'is_participating']
    list_filter = ['is_participating']


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['seller', 'purchase_request', 'status', 'submitted_at']
    list_filter = ['status']
