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

        # If no new file uploaded
        if not rfq:
            # If creating (no instance yet) → required
            if not self.instance.pk:
                raise forms.ValidationError('You must upload an RFQ file.')
            # If editing → allow existing file
            return rfq

        # If file exists, validate it
        if hasattr(rfq, 'size') and rfq.size == 0:
            raise forms.ValidationError('Your uploaded RFQ file is empty.')

        content_type = getattr(rfq, 'content_type', None)
        if content_type and content_type != 'application/pdf':
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

class AmountInPage(forms.Form):
    """Dictate how many purchase requests per page."""

    dictate = forms.IntegerField(
        required=False,
        label="Set item count per page:",
        widget=forms.NumberInput(
            attrs={"min_value" : 1}
        )
    )

class UpdatePurchaseRequestDeadline(forms.ModelForm):
    # Activity Things
    closing_deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M"
        )
    )

    class Meta:
        model = PurchaseRequest
        fields = ["closing_deadline"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.closing_deadline:
            local_dt = timezone.localtime(self.instance.closing_deadline)
            self.initial["closing_deadline"] = local_dt.strftime("%Y-%m-%dT%H:%M")

    def clean_closing_deadline(self):
        dt = self.cleaned_data["closing_deadline"]

        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())

        return dt


class SearchFilterForm(forms.Form):
    CATEGORY_CHOICES = [('', 'All Categories')] + PurchaseRequest.CATEGORY_CHOICES

    keyword    = forms.CharField(required=False, label='Search')
    category   = forms.ChoiceField(required=False, choices=CATEGORY_CHOICES, label='Category')
    budget_min = forms.DecimalField(required=False, label='Budget min', min_value=0)
    budget_max = forms.DecimalField(required=False, label='Budget max', min_value=0)
    area       = forms.CharField(required=False, label='Area of delivery')
    deadline   = forms.DateField(required=False, label='Deadline on or before',
                                 widget=forms.DateInput(attrs={'type': 'date'}))
