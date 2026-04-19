from django import forms
from django.utils import timezone
from .models import Listing, ConsumerRequest, BusinessResponse, ListingTransaction, Review


class CreateListing(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = ['business', 'created_at', 'updated_at', 'availability', 'view_count']
    
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

    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')

        if min_price and max_price:
            if min_price > max_price:
                raise forms.ValidationError(
                    'The minimum price must be lesser than or equal to the maximum price.'
                )

        return cleaned_data

class CreateListingTransaction(forms.ModelForm):
    class Meta:
        model = ListingTransaction
        exclude = ['listing', 'consumer', 'created_at', 'transaction_type']

class ChooseTransactionKind(forms.Form):
    TRANSACTION_KIND = [('listing','From Listings'),('consumer_request','From Consumer Request')]
    CATEGORY_CHOICES = [('','All Categories'),('goods', 'Goods'),('services', 'Services'),('custom', 'Custom')]

    keyword       = forms.CharField(required=False, label='Search')
    category      = forms.ChoiceField(required=False, choices=CATEGORY_CHOICES, label='Category')
    person        = forms.CharField(required=False)
    min_price     = forms.DecimalField(required=False, label='Min Price', min_value=0)
    max_price     = forms.DecimalField(required=False, label='Max Price', min_value=0)
    earliest_date = forms.DateTimeField(required=False)
    latest_date   = forms.DateTimeField(required=False)
    transaction   = forms.ChoiceField(required=False, choices=TRANSACTION_KIND, label='Kind of Transaction')

    class Meta:
        widgets = {
            'earliest_date': forms.DateTimeInput(
                attrs={'type':'datetime-local'}
            ),
            'latest_date': forms.DateTimeInput(
                attrs={'type':'datetime-local'}
            )
        }

class CreateConsumerRequest(forms.ModelForm):
    class Meta:
        model = ConsumerRequest
        exclude = ['consumer', 'created_at', 'updated_at', 'response_count', 'status']
        widgets = {
            'needed_by': forms.DateTimeInput(
                attrs={'type':'datetime-local'}
            )
        }

    def clean_needed_by(self):
        needed_by = self.cleaned_data.get('needed_by')
        
        if needed_by <= timezone.now():
            raise forms.ValidationError(
                'The needed date and time must be in the future.'
            )
        return needed_by
    
    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')

        if min_price and max_price:
            if min_price > max_price:
                raise forms.ValidationError(
                    'The minimum price must be lesser than or equal to the maximum price.'
                )

        return cleaned_data

class RespondToRequest(forms.ModelForm):
    class Meta:
        model = BusinessResponse
        exclude = ['business', 'consumer_request', 'created_at', 'updated_at']
        widgets = {
            'earliest_delivery': forms.DateTimeInput(
                attrs={'type':'datetime-local'}
            ),
            'latest_delivery': forms.DateTimeInput(
                attrs={'type':'datetime-local'}
            )
        }

    def clean_earliest_delivery(self):
        earliest_delivery = self.cleaned_data.get('earliest_delivery')  
        
        if earliest_delivery <= timezone.now():
            raise forms.ValidationError(
                'The needed date and time must be in the future.'
            )

        return earliest_delivery

    def clean_latest_delivery(self):
        latest_delivery = self.cleaned_data.get('latest_delivery')
        
        if latest_delivery <= timezone.now():
            raise forms.ValidationError(
                'The needed date and time must be in the future.'
            )

        return latest_delivery

    def clean(self):
        cleaned_data = super().clean()
        earliest_delivery = cleaned_data.get('earliest_delivery')
        latest_delivery = cleaned_data.get('latest_delivery')

        if earliest_delivery and latest_delivery:
            if earliest_delivery > latest_delivery:
                raise forms.ValidationError(
                    'Rearrange the dates and times'
                )
        
        return cleaned_data

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

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        exclude = ['transaction','created_at','updated_at']

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
    delivery_area = forms.CharField(required=False, label='Area of Delivery')

class AmountInPage(forms.Form):
    """Dictate how many objects per page."""

    dictate = forms.IntegerField(
        required=False,
        label="Set item count per page:",
        widget=forms.NumberInput(
            attrs={"min_value" : 1}
        )
    )