from django import forms
from .models import Listing, BusinessResponse


class CreateListing(forms.ModelForm):
    images = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False
    )

    class Meta:
        model = Listing
        exclude = ['business', 'created_at', 'updated_at', 'availability']


class RespondToRequest(forms.ModelForm):
    class Meta:
        model = BusinessResponse
        exclude = ['business', 'consumer_request', 'created_at', 'updated_at']
