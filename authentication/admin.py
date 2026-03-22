from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Client, BusinessProfile, ConsumerProfile, OTP


@admin.register(Client)
class ClientAdmin(UserAdmin):
    list_display = ['username', 'email', 'account_type', 'is_active', 'date_joined']
    list_filter = ['account_type', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Account Info', {'fields': ('account_type', 'contact_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Account Info', {'fields': ('email', 'account_type', 'contact_number')}),
    )


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'client', 'status', 'business_type', 'created_at']
    list_filter = ['status', 'business_type']
    search_fields = ['business_name', 'tin']


@admin.register(ConsumerProfile)
class ConsumerProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'client', 'created_at']


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['client', 'code', 'created_at', 'expires_at', 'is_used', 'attempts']
    list_filter = ['is_used']
