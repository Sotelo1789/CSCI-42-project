from django import forms
from .models import PurchaseRequest

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
            attrs={"type": "datetime-local"}
        )
    )

    class Meta:
        model = PurchaseRequest
        fields = ["closing_deadline"]