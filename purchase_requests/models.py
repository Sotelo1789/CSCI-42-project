from django.db import models
from django.conf import settings
from django.utils import timezone


class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    CATEGORY_CHOICES = [
        ('goods', 'Goods'),
        ('services', 'Services'),
        ('equipment', 'Equipment'),
        ('construction', 'Construction'),
        ('it', 'IT & Technology'),
        ('other', 'Other'),
    ]

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_purchase_requests'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    area_of_delivery = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=15, decimal_places=2)
    closing_deadline = models.DateTimeField()
    rfq_file = models.FileField(upload_to='uploads/rfq/', null=False, blank=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'purchase_request'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_open(self):
        return self.status == 'open' and timezone.now() < self.closing_deadline

    @property
    def is_past_deadline(self):
        return timezone.now() >= self.closing_deadline


class Participation(models.Model):
    """Tracks which sellers have joined a purchase request (Review Purchase Request list)."""
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='participations'
    )
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name='participations'
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    is_participating = models.BooleanField(default=False)  # True after clicking "Participate"

    class Meta:
        db_table = 'participation'
        unique_together = ('seller', 'purchase_request')

    def __str__(self):
        return f'{self.seller.username} -> {self.purchase_request.title}'


class Offer(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='offers'
    )
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name='offers'
    )
    offer_file = models.FileField(upload_to='uploads/offers/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'offer'
        unique_together = ('seller', 'purchase_request')
        ordering = ['-submitted_at']

    def __str__(self):
        return f'Offer by {self.seller.username} for {self.purchase_request.title}'
