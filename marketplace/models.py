from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

def validate_nonnegative(value):
    if not value>=0:
        raise ValidationError("Value can't be below 0")


def validate_rating(value):
    if not (value>=1 and value<=10):
        raise ValidationError("Scale of 1-10 only")


class Listing(models.Model):
    CATEGORY_CHOICES = [
        ('goods', 'Goods'),
        ('services', 'Services'),
        ('custom', 'Custom'),
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
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='custom')
    min_price = models.DecimalField(max_digits=15, decimal_places=2, validators=[validate_nonnegative])
    max_price = models.DecimalField(max_digits=15, decimal_places=2, validators=[validate_nonnegative])
    quantity = models.IntegerField(validators=[validate_nonnegative])
    unit = models.CharField(max_length=10)
    delivery_option = models.CharField(max_length=10, choices=DELIVERY_CHOICES)
    delivery_area = models.CharField(max_length=100)
    delivery_time = models.IntegerField() # assumes delivery time is in number of days
    terms_conditions = models.FileField(upload_to='uploads/listings/termsconditions', null=False, blank=False)
    availability = models.BooleanField(default=True)
    view_count = models.IntegerField(validators=[validate_nonnegative], default=0)
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
    order = models.IntegerField(validators=[validate_nonnegative])
    is_primary = models.BooleanField(default=False)


class ConsumerRequest(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ]

    CATEGORY_CHOICES = [
        ('goods', 'Goods'),
        ('services', 'Services'),
        ('custom', 'Custom'),
    ]

    consumer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='marketplace_request'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='custom')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    min_price = models.DecimalField(max_digits=15, decimal_places=2, validators=[validate_nonnegative])
    max_price = models.DecimalField(max_digits=15, decimal_places=2, validators=[validate_nonnegative])
    delivery_area = models.CharField(max_length=100)
    needed_by = models.DateTimeField()
    response_count = models.IntegerField(validators=[validate_nonnegative], default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'consumer_request'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


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
    price = models.DecimalField(max_digits=15, decimal_places=2, validators=[validate_nonnegative])
    earliest_delivery = models.DateTimeField()
    latest_delivery = models.DateTimeField()
    quotation = models.FileField(upload_to='uploads/quotations/', null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'business_response'
        ordering = ['-created_at']

    def __str__(self):
        return f'Response of {self.business.username} to {self.consumer_request.title}'


class ConsumerRequestImage(models.Model):
    consumer_request = models.ForeignKey(
        ConsumerRequest,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='uploads/consumer_requests/images/')


class Transaction(models.Model):
    price = models.DecimalField(max_digits=15, decimal_places=2, validators=[validate_nonnegative])
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=1)


class ListingTransaction(Transaction):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='listing_transaction'
    )
    consumer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listing_transaction'
    )


class ConsumerRequestTransaction(Transaction):
    consumer_request = models.ForeignKey(
        ConsumerRequest,
        on_delete=models.CASCADE,
        related_name='consumer_request_transaction'
    )
    business_response = models.ForeignKey(
        BusinessResponse,
        on_delete=models.CASCADE,
        related_name='consumer_request_transaction'
    )


class FavoriteListing(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='favorite_listing'
    )
    consumer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_listing'
    )
    added_favorite_date = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='review',
        blank=True,
        null=True
    )
    
    text = models.TextField()
    rating = models.IntegerField(validators=[validate_rating])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)