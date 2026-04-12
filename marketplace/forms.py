from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Listing, BusinessResponse


class CreateListing(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = ['business', 'created_at', 'updated_at', 'availability']
        
    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        tc = cleaned_data.get('terms_conditions')

        if min_price > max_price:
            raise forms.ValidationError(
                'The minimum price must be lesser than or equal to the maximum price.'
            )

        if not tc:
            if not self.instance.pk:
                raise forms.ValidationError('You must upload your terms and conditions.')

        if hasattr(tc, 'size') and tc.size == 0:
            raise forms.ValidationError('Your uploaded file is empty.')

        content_type = getattr(tc, 'content_type', None)
        if content_type and content_type != 'application/pdf':
            raise forms.ValidationError('Your uploaded terms and conditions must be a PDF.')

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

    def clean(self):
        cleaned_data = super().clean()
        earliest_delivery = cleaned_data.get('earliest_delivery')
        latest_delivery = cleaned_data.get('latest_delivery')
        quotation = cleaned_data.get('quotation')

        if earliest_delivery > latest_delivery:
            raise ValidationError("Latest delivery cannot be earlier than earliest delivery.")

        if earliest_delivery < timezone.now():
            raise ValidationError("Earliest delivery cannot be in the past.")
        
        if quotation:
            if hasattr(quotation, 'size') and quotation.size == 0:
                raise forms.ValidationError('Your uploaded file is empty.')

            content_type = getattr(quotation, 'content_type', None)
            if content_type and content_type != 'application/pdf':
                raise forms.ValidationError('Your uploaded quotation must be a PDF.')
            
        return cleaned_data


class RequestSearchFilter(forms.Form):
    CATEGORY_CHOICES = [('', 'All Categories')] + Listing.CATEGORY_CHOICES

    keyword   = forms.CharField(required=False, label='Search')
    category  = forms.ChoiceField(required=False, choices=CATEGORY_CHOICES, label='Category')
    min_price = forms.DecimalField(required=False, label='Price min', min_value=0)
    max_price = forms.DecimalField(required=False, label='Price max', min_value=0)
    area      = forms.CharField(required=False, label='Area of delivery')
