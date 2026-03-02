from django import forms
from django.utils import timezone
from .models import PurchaseRequest, Offer


class CreatePurchaseRequest(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        exclude = ['buyer', 'status', 'created_at', 'updated_at']
        widgets = {
            'closing_deadline': forms.DateTimeInput(
                attrs={'type':'datetime-local'}
            )
        }
    
    def clean_closing_deadline(self):
        closing_deadline = self.cleaned_data.get('closing_deadline')

        if closing_deadline <= timezone.now():
            raise forms.ValidationError(
                'The closing date and time must be in the future.'
            )
        
        return closing_deadline
        
    def clean_rfq_file(self):
        rfq = self.cleaned_data.get('rfq_file')

        if not rfq:
            raise forms.ValidationError('You must upload an RFQ file.')
        if rfq.size == 0:
            raise forms.ValidationError('Your uplaoded RFQ file is empty.')
        if rfq.content_type != 'application/pdf':
            raise forms.ValidationError('Your uploaded RFQ file must be a PDF.')
        
        return rfq


class SubmitOffer(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['offer_file']

    def clean_offer_file(self):
        pdf = self.cleaned_data.get('offer_file')

        if not pdf:
            raise forms.ValidationError('No file uploaded.')
        if pdf.size == 0:
            raise forms.ValidationError('Uploaded file is empty.')
        if pdf.content_type != 'application/pdf':
            raise forms.ValidationError('File must be a PDF.')
        
        return pdf
