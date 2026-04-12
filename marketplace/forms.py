from django import forms
from .models import Listing, BusinessResponse


class CreateListing(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = ['business', 'created_at', 'updated_at', 'availability', 'view_count']
        
    def validate_price_range(self):
        min_price = self.cleaned_data.get('min_price')
        max_price = self.cleaned_data.get('max_price')

        if min_price > max_price:
            raise forms.ValidationError(
                'The minimum price must be lesser than or equal to the maximum price.'
            )


class RespondToRequest(forms.ModelForm):
    class Meta:
        model = BusinessResponse
        exclude = ['business', 'consumer_request', 'created_at', 'updated_at']


class SearchFilterForm(forms.Form):
    CATEGORY_CHOICES = [('', 'All Categories')] + Listing.CATEGORY_CHOICES
    AVAILABILITY_CHOICES = [(None,'All Existing Listings'),('true','Available'),('false','Unavailable')]

    keyword   = forms.CharField(required=False, label='Search')
    category  = forms.ChoiceField(required=False, choices=CATEGORY_CHOICES, label='Category')
    min_price = forms.DecimalField(required=False, label='Price min', min_value=0)
    max_price = forms.DecimalField(required=False, label='Price max', min_value=0)
    area      = forms.CharField(required=False, label='Area of delivery')
    rating    = forms.IntegerField(required=False, label='Business rating min', min_value=1, max_value=10)
    availability = forms.ChoiceField(required=False, choices=AVAILABILITY_CHOICES, label='Availability')

class AmountInPage(forms.Form):
    """Dictate how many objects per page."""

    dictate = forms.IntegerField(
        required=False,
        label="Set item count per page:",
        widget=forms.NumberInput(
            attrs={"min_value" : 1}
        )
    )