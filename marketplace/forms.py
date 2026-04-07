from django import forms
from .models import Listing, BusinessResponse


class CreateListing(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = ['business', 'created_at', 'updated_at', 'availability']


class RespondToRequest(forms.ModelForm):
    class Meta:
        model = BusinessResponse
        exclude = ['business', 'consumer_request', 'created_at', 'updated_at']
