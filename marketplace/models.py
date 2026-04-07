from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from authentication.models import BusinessProfile


class Listing(models.Model):
    CATEGORY_CHOICES = [
        ('temp', 'Temporary Category')
    ]

    DELIVERY_CHOICES = [
        ('pickup', 'Pickup'),
        ('delivery', 'Delivery'),
        ('shipping', 'Shipping')
    ]

    business = models.ForeignKey(
        BusinessProfile,
        on_delete=models.CASCADE,
        related_name='listings'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    min_price = models.DecimalField(max_digits=15, decimal_places=2)
    max_price = models.DecimalField(max_digits=15, decimal_places=2)
    unit = models.CharField(max_length=10)
    delivery = models.CharField(max_length=10, choices=DELIVERY_CHOICES)
    delivery_areas = models.ArrayField(models.CharField(max_length=100))
    delivery_time = models.IntegerField() # assumes delivery time is in number of days
    terms_conditions = models.FileField(upload_to='uploads/listings/termsconditions')
    availability = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'listing'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ListingImage(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='uploads/listings/images/')


class ConsumerRequest(models.Model):
    # INCOMPLETE
    CATEGORY_CHOICES = [
        ('temp', 'Temporary Category')
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    min_budget = models.DecimalField(max_digits=15, decimal_places=2)
    max_budget = models.DecimalField(max_digits=15, decimal_places=2)
    #etc


class BusinessResponse(models.Model):
    business = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    consumer_request = models.ForeignKey(
        ConsumerRequest,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    message = models.TextField()
    price = models.DecimalField(max_digits=15, decimal_places=2)
    quotation = models.FileField(upload_to='uploads/quotations/')
