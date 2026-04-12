from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from marketplace.models import Listing, BusinessResponse, ListingTransaction, ConsumerRequestTransaction, Review


class ClientManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('account_type', 'admin')
        return self.create_user(username, email, password, **extra_fields)


class Client(AbstractBaseUser, PermissionsMixin):
    ACCOUNT_TYPE_CHOICES = [
        ('business', 'Business'),
        ('consumer', 'Consumer'),
        ('admin', 'Admin'),
    ]

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    contact_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = ClientManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'client'
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return f'{self.username} ({self.account_type})'

    @property
    def is_business(self):
        return self.account_type == 'business'

    @property
    def is_consumer(self):
        return self.account_type == 'consumer'


class BusinessProfile(models.Model):
    BUSINESS_TYPE_CHOICES = [
        ('trading', 'Trading'),
        ('servicing', 'Servicing'),
        ('manufacturing', 'Manufacturing'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    client = models.OneToOneField(
        Client, on_delete=models.CASCADE, related_name='business_profile'
    )
    business_name = models.CharField(max_length=255)
    business_address = models.TextField()
    tin = models.CharField(max_length=20, unique=True, verbose_name='TIN')
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPE_CHOICES)

    # Authorized representative
    rep_name = models.CharField(max_length=255, verbose_name='Representative Name')
    rep_position = models.CharField(max_length=100, verbose_name='Representative Position')
    rep_contact = models.CharField(max_length=20, verbose_name='Representative Contact')

    # Documents
    mayors_permit = models.FileField(upload_to='uploads/business_docs/', null=True, blank=True)
    sec_certificate = models.FileField(upload_to='uploads/business_docs/', null=True, blank=True)
    bir_certificate = models.FileField(upload_to='uploads/business_docs/', null=True, blank=True)
    tax_clearance = models.FileField(upload_to='uploads/business_docs/', null=True, blank=True)
    other_documents = models.FileField(upload_to='uploads/business_docs/', null=True, blank=True)

    # Approval
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'business_profile'

    def __str__(self):
        return self.business_name

    def update_rate(self):
        listing_transactions = ListingTransaction.objects.filter(listing__business=self.client)
        consumer_request_transactions = ConsumerRequestTransaction.objects.filter(business_response__business=self.client)
        total_reviewed_transactions = 0
        final_rating = 0
        for ltransaction in listing_transactions:
            try:
                review = Review.objects.get(listing_transaction=ltransaction)
            except Review.DoesNotExist:
                review = None
            if review is not None:
                final_rating += review.rating
                total_reviewed_transactions += 1
        for crtransaction in consumer_request_transactions:
            try:
                review = Review.objects.get(consumer_request_transaction=crtransaction)
            except Review.DoesNotExist:
                review = None
            if review is not None:
                final_rating += review.rating
                total_reviewed_transactions += 1
        if(total_reviewed_transactions != 0):
            final_rating = float(final_rating) / float(total_reviewed_transactions)
            self.rating = final_rating
        self.save()


class ConsumerProfile(models.Model):
    client = models.OneToOneField(
        Client, on_delete=models.CASCADE, related_name='consumer_profile'
    )
    full_name = models.CharField(max_length=255)
    address = models.TextField()
    government_id = models.ImageField(upload_to='uploads/consumer_docs/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'consumer_profile'

    def __str__(self):
        return self.full_name


class OTP(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)

    class Meta:
        db_table = 'otp'
        ordering = ['-created_at']

    def __str__(self):
        return f'OTP for {self.client.email}'

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        from django.conf import settings
        max_attempts = getattr(settings, 'OTP_MAX_ATTEMPTS', 5)
        return not self.is_used and not self.is_expired and self.attempts < max_attempts
