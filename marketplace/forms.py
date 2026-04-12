from django import forms
from .models import Listing, ConsumerRequest, BusinessResponse


class CreateListing(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = ['business', 'created_at', 'updated_at', 'availability', 'view_count']
        
    def clean_price_range(self):
        min_price = self.cleaned_data.get('min_price')
        max_price = self.cleaned_data.get('max_price')

        if min_price > max_price:
            raise forms.ValidationError(
                'The minimum price must be lesser than or equal to the maximum price.'
            )
    
    def clean_toc(self):
        toc = self.cleaned_data.get('terms_conditions')

        # If no new file uploaded
        if not toc:
            # If creating (no instance yet) → required
            if not self.instance.pk:
                raise forms.ValidationError('You must upload a TOC file.')
            # If editing → allow existing file
            return toc

        # If file exists, validate it
        if hasattr(toc, 'size') and toc.size == 0:
            raise forms.ValidationError('Your uploaded TOC file is empty.')

        content_type = getattr(toc, 'content_type', None)
        if content_type and content_type != 'application/pdf':
            raise forms.ValidationError('Your uploaded TOC file must be a PDF.')

        return toc

class CreateConsumerRequest(forms.ModelForm):
    class Meta:
        model = ConsumerRequest
        exclude = ['consumer', 'created_at', 'updated_at', 'response_count', 'status']
        
    def clean_price_range(self):
        min_price = self.cleaned_data.get('price_min')
        max_price = self.cleaned_data.get('price_max')

        if min_price > max_price:
            raise forms.ValidationError(
                'The minimum price must be lesser than or equal to the maximum price.'
            )

class CreateConsumerRequest(forms.ModelForm):
    class Meta:
        model = ConsumerRequest
        exclude = ['consumer', 'created_at', 'updated_at', 'response_count', 'status']
        

class RespondToRequest(forms.ModelForm):
    class Meta:
        model = BusinessResponse
        exclude = ['business', 'consumer_request', 'created_at', 'updated_at']

    def clean_quotation(self):
        quotation = self.cleaned_data.get('quotation')

        # If no new file uploaded
        if not quotation:
            # If creating (no instance yet) → required
            if not self.instance.pk:
                raise forms.ValidationError('You must upload a quotation file.')
            # If editing → allow existing file
            return quotation

        # If file exists, validate it
        if hasattr(quotation, 'size') and quotation.size == 0:
            raise forms.ValidationError('Your uploaded quotation file is empty.')

        content_type = getattr(quotation, 'content_type', None)
        if content_type and content_type != 'application/pdf':
            raise forms.ValidationError('Your uploaded quotation file must be a PDF.')

        return quotation

class ListingSearchFilterForm(forms.Form):
    CATEGORY_CHOICES = [('', 'All Categories')] + Listing.CATEGORY_CHOICES
    AVAILABILITY_CHOICES = [(None,'All Existing Listings'),('true','Available'),('false','Unavailable')]

    keyword   = forms.CharField(required=False, label='Search')
    category  = forms.ChoiceField(required=False, choices=CATEGORY_CHOICES, label='Category')
    min_price = forms.DecimalField(required=False, label='Price min', min_value=0)
    max_price = forms.DecimalField(required=False, label='Price max', min_value=0)
    area      = forms.CharField(required=False, label='Area of delivery')
    rating    = forms.IntegerField(required=False, label='Business rating min', min_value=1, max_value=10)
    availability = forms.ChoiceField(required=False, choices=AVAILABILITY_CHOICES, label='Availability')

class RequestSearchFilterForm(forms.Form):
    CATEGORY_CHOICES = [('', 'All Categories')] + ConsumerRequest.CATEGORY_CHOICES
    AVAILABILITY_CHOICES = [(None,'All Existing Listings'),('true','Available'),('false','Unavailable')]

    keyword   = forms.CharField(required=False, label='Search')
    category  = forms.ChoiceField(required=False, choices=CATEGORY_CHOICES, label='Category')
    min_price = forms.DecimalField(required=False, label='Price min', min_value=0)
    max_price = forms.DecimalField(required=False, label='Price max', min_value=0)

class AmountInPage(forms.Form):
    """Dictate how many objects per page."""

    dictate = forms.IntegerField(
        required=False,
        label="Set item count per page:",
        widget=forms.NumberInput(
            attrs={"min_value" : 1}
        )
    )