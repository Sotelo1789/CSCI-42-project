from django.db import models
from django.conf import settings


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
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    min_price = models.DecimalField(max_digits=15, decimal_places=2)
    max_price = models.DecimalField(max_digits=15, decimal_places=2)
    unit = models.CharField(max_length=10)
    delivery_option = models.CharField(max_length=10, choices=DELIVERY_CHOICES)
    delivery_area = models.CharField(max_length=100)
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
    CATEGORY_CHOICES = [
        ('temp', 'Temporary Category')
    ]

    CONTACT_CHOICES = [
        ('message', 'Message'),
        ('email', 'Email'),
        ('phone', "Phone")
    ]

    STATUS_CHOICES = [
        ('none', 'No Responses'),
        ('response', 'Received Responses'),
        ('closed', 'Closed')
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    min_budget = models.DecimalField(max_digits=15, decimal_places=2)
    max_budget = models.DecimalField(max_digits=15, decimal_places=2)
    delivery_area = models.CharField(max_length=100)
    needed_by = models.DateTimeField()
    contact_pref = models.CharField(max_length=10, choices=CONTACT_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='none')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'request'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class RequestImage(models.Model):
    request = models.ForeignKey(
        ConsumerRequest,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='uploads/requests/images/')


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
    earliest_delivery = models.DateTimeField()
    latest_delivery = models.DateTimeField()
    quotation = models.FileField(upload_to='uploads/quotations/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'business_response'
        ordering = ['-created_at']

    def __str__(self):
        return f'Response of {self.business.username} to {self.consumer_request.title}'
