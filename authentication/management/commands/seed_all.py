"""
Seed command — creates all sample accounts and data for testing.

Usage:
    python3 manage.py seed_all

Creates:
  - 1 admin superuser
  - 3 business accounts (approved)
  - 2 consumer accounts
  - Listings, consumer requests, purchase requests, responses, transactions
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import os, shutil

from authentication.models import Client, BusinessProfile, ConsumerProfile
from marketplace.models import (
    Listing, ConsumerRequest, BusinessResponse,
    ListingTransaction, ConsumerRequestTransaction,
)
from purchase_requests.models import PurchaseRequest


class Command(BaseCommand):
    help = 'Seed the database with sample accounts and data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...\n')

        # ── ADMIN ────────────────────────────────────────────────────────────
        admin = self._make_user(
            username='admin',
            email='admin@proc.ph',
            password='admin1234',
            account_type='admin',
            is_staff=True,
            is_superuser=True,
        )
        self.stdout.write(f'  admin: admin / admin1234')

        # ── BUSINESSES ───────────────────────────────────────────────────────
        b1 = self._make_user('techsupply', 'techsupply@proc.ph', 'password123', 'business')
        bp1, _ = BusinessProfile.objects.get_or_create(client=b1, defaults=dict(
            business_name='TechSupply PH',
            business_address='123 Ayala Ave, Makati City',
            tin='123-456-789-000',
            business_type='trading',
            rep_name='Ana Reyes',
            rep_position='CEO',
            rep_contact='09171234567',
            status='approved',
        ))

        b2 = self._make_user('officegoods', 'officegoods@proc.ph', 'password123', 'business')
        bp2, _ = BusinessProfile.objects.get_or_create(client=b2, defaults=dict(
            business_name='Office Goods Corp',
            business_address='456 EDSA, Quezon City',
            tin='987-654-321-000',
            business_type='trading',
            rep_name='Ben Santos',
            rep_position='Operations Manager',
            rep_contact='09189876543',
            status='approved',
        ))

        b3 = self._make_user('builditph', 'builditph@proc.ph', 'password123', 'business')
        bp3, _ = BusinessProfile.objects.get_or_create(client=b3, defaults=dict(
            business_name='Build It PH',
            business_address='789 Commonwealth Ave, Quezon City',
            tin='111-222-333-444',
            business_type='servicing',
            rep_name='Carlo Dela Cruz',
            rep_position='Director',
            rep_contact='09201112222',
            status='approved',
        ))

        self.stdout.write(f'  business 1: techsupply / password123  ({bp1.business_name})')
        self.stdout.write(f'  business 2: officegoods / password123  ({bp2.business_name})')
        self.stdout.write(f'  business 3: builditph / password123  ({bp3.business_name})')

        # ── CONSUMERS ────────────────────────────────────────────────────────
        c1 = self._make_user('juandelacruz', 'juan@proc.ph', 'password123', 'consumer')
        ConsumerProfile.objects.get_or_create(client=c1, defaults=dict(
            full_name='Juan Dela Cruz',
            address='12 Mabini St, Manila',
            government_id='uploads/consumer_docs/placeholder.jpg',
        ))

        c2 = self._make_user('mariasantos', 'maria@proc.ph', 'password123', 'consumer')
        ConsumerProfile.objects.get_or_create(client=c2, defaults=dict(
            full_name='Maria Santos',
            address='34 Rizal Ave, Pasig City',
            government_id='uploads/consumer_docs/placeholder.jpg',
        ))

        self.stdout.write(f'  consumer 1: juandelacruz / password123')
        self.stdout.write(f'  consumer 2: mariasantos / password123')

        # ── LISTINGS ─────────────────────────────────────────────────────────
        # Need a dummy file for terms_conditions (required non-null)
        dummy_path = self._dummy_file()

        l1 = Listing.objects.create(
            business=b1,
            title='Laptop Computers — Dell Latitude Series',
            description='Brand new Dell Latitude laptops. Intel Core i5, 16GB RAM, 512GB SSD. Ideal for corporate use. Bulk orders welcome.',
            category='goods',
            min_price=45000,
            max_price=65000,
            quantity=50,
            unit='unit',
            delivery_option='delivery',
            delivery_area='Metro Manila',
            delivery_time=7,
            terms_conditions=dummy_path,
            availability=True,
        )

        l2 = Listing.objects.create(
            business=b2,
            title='Office Supplies Bundle — A4 Paper, Pens, Folders',
            description='Complete office supplies bundle. Includes 10 reams A4 bond paper, 24 ballpoint pens, and 20 clear folders.',
            category='goods',
            min_price=800,
            max_price=1200,
            quantity=200,
            unit='bundle',
            delivery_option='delivery',
            delivery_area='NCR',
            delivery_time=3,
            terms_conditions=dummy_path,
            availability=True,
        )

        l3 = Listing.objects.create(
            business=b3,
            title='IT Infrastructure Setup Service',
            description='Full office network setup including router installation, cable management, and network configuration. Up to 20 workstations.',
            category='services',
            min_price=15000,
            max_price=35000,
            quantity=1,
            unit='package',
            delivery_option='pickup',
            delivery_area='Metro Manila and nearby provinces',
            delivery_time=14,
            terms_conditions=dummy_path,
            availability=True,
        )

        l4 = Listing.objects.create(
            business=b1,
            title='Wireless Mouse and Keyboard Combo',
            description='Logitech MK270 Wireless Combo. 2.4GHz wireless, plug-and-play USB receiver. Available in bulk.',
            category='goods',
            min_price=800,
            max_price=1100,
            quantity=150,
            unit='unit',
            delivery_option='shipping',
            delivery_area='Nationwide',
            delivery_time=5,
            terms_conditions=dummy_path,
            availability=True,
        )

        self.stdout.write(f'  created {Listing.objects.count()} listings')

        # ── CONSUMER REQUESTS ────────────────────────────────────────────────
        cr1 = ConsumerRequest.objects.create(
            consumer=c1,
            title='Looking for office chairs — ergonomic, qty 10',
            description='Need 10 ergonomic office chairs for our small office. Must have lumbar support and adjustable height. Budget is flexible.',
            category='goods',
            status='open',
            min_price=3000,
            max_price=8000,
            delivery_area='Makati City',
            needed_by=timezone.now() + timedelta(days=30),
            contact_pref='email',
        )

        cr2 = ConsumerRequest.objects.create(
            consumer=c2,
            title='Website development for small business',
            description='Need a simple 5-page website for my bakery. Must be mobile-friendly with online ordering. Looking for affordable options.',
            category='services',
            status='open',
            min_price=10000,
            max_price=25000,
            delivery_area='Quezon City',
            needed_by=timezone.now() + timedelta(days=45),
            contact_pref='email',
        )

        cr3 = ConsumerRequest.objects.create(
            consumer=c1,
            title='Printer cartridges — HP 680 black and color, x20',
            description='Need 20 sets of HP 680 ink cartridges (black and color combo). Must be original HP, not compatible.',
            category='goods',
            status='open',
            min_price=400,
            max_price=700,
            delivery_area='Manila',
            needed_by=timezone.now() + timedelta(days=14),
            contact_pref='phone',
        )

        self.stdout.write(f'  created {ConsumerRequest.objects.count()} consumer requests')

        # ── PURCHASE REQUESTS ────────────────────────────────────────────────
        pr1 = PurchaseRequest.objects.create(
            buyer=b1,
            title='Steel pipes — schedule 40, 2-inch diameter, 100 lengths',
            description='Procurement of 100 lengths of Schedule 40 steel pipes, 2-inch diameter, 6 meters each. For a construction project in Laguna.',
            category='construction',
            area_of_delivery='Laguna',
            budget=180000,
            closing_deadline=timezone.now() + timedelta(days=14),
            status='open',
        )

        pr2 = PurchaseRequest.objects.create(
            buyer=b2,
            title='Annual software license renewal — Microsoft 365 Business',
            description='Renewing Microsoft 365 Business Standard licenses for 25 users. Requires volume licensing with invoice.',
            category='it',
            area_of_delivery='Quezon City',
            budget=120000,
            closing_deadline=timezone.now() + timedelta(days=21),
            status='open',
        )

        pr3 = PurchaseRequest.objects.create(
            buyer=b1,
            title='Janitorial supplies — monthly restock for 3 floors',
            description='Monthly procurement of janitorial supplies for a 3-floor office building. Includes trash bags, disinfectants, mop heads, and cleaning solutions.',
            category='goods',
            area_of_delivery='Makati City',
            budget=25000,
            closing_deadline=timezone.now() + timedelta(days=7),
            status='open',
        )

        pr4 = PurchaseRequest.objects.create(
            buyer=b3,
            title='Branded corporate uniforms — polo shirts, 50 pcs',
            description='50 pieces of embroidered polo shirts with company logo. Sizes: S to XL. Preferred colors: navy blue or dark green.',
            category='goods',
            area_of_delivery='Quezon City',
            budget=45000,
            closing_deadline=timezone.now() + timedelta(days=30),
            status='open',
        )

        pr5 = PurchaseRequest.objects.create(
            buyer=b2,
            title='CCTV installation — 8-camera system, 2 floors',
            description='Supply and installation of an 8-camera CCTV system across 2 floors. Must include NVR, 2TB storage, and remote viewing setup.',
            category='it',
            area_of_delivery='EDSA, Quezon City',
            budget=80000,
            closing_deadline=timezone.now() - timedelta(days=3),  # already closed
            status='closed',
        )

        self.stdout.write(f'  created {PurchaseRequest.objects.count()} purchase requests')

        # ── BUSINESS RESPONSES (to consumer requests) ────────────────────────
        br1 = BusinessResponse.objects.create(
            business=b2,
            consumer_request=cr1,
            price=5500,
            message='We can supply 10 ergonomic chairs from our Herman Miller range. Delivery within Metro Manila in 5–7 business days. Free delivery for this order.',
            earliest_delivery=timezone.now() + timedelta(days=5),
            latest_delivery=timezone.now() + timedelta(days=10),
        )
        cr1.response_count += 1
        cr1.save()

        br2 = BusinessResponse.objects.create(
            business=b3,
            consumer_request=cr1,
            price=4200,
            message='Offering mid-range ergonomic chairs with lumbar support. Can do bulk discount for 10 units. Delivery in 3–5 days.',
            earliest_delivery=timezone.now() + timedelta(days=3),
            latest_delivery=timezone.now() + timedelta(days=7),
        )
        cr1.response_count += 1
        cr1.save()

        br3 = BusinessResponse.objects.create(
            business=b1,
            consumer_request=cr3,
            price=580,
            message='We have original HP 680 cartridges in stock. Can ship same day for orders placed before 2PM. 20 sets available.',
            earliest_delivery=timezone.now() + timedelta(days=1),
            latest_delivery=timezone.now() + timedelta(days=3),
        )
        cr3.response_count += 1
        cr3.save()

        self.stdout.write(f'  created {BusinessResponse.objects.count()} business responses')

        # ── COMPLETED TRANSACTION (listing purchase) ─────────────────────────
        # With MTI, create the child directly — Django creates the parent row automatically
        lt1 = ListingTransaction.objects.create(
            price=950,
            transaction_type='L',
            listing=l2,
            consumer=c1,
        )

        self.stdout.write(f'  created 1 completed listing transaction')

        self.stdout.write(self.style.SUCCESS('\n✓ Seed complete. Login details:\n'))
        self.stdout.write('  Role       | Username       | Password')
        self.stdout.write('  -----------|----------------|----------')
        self.stdout.write('  Admin      | admin          | admin1234')
        self.stdout.write('  Business 1 | techsupply     | password123')
        self.stdout.write('  Business 2 | officegoods    | password123')
        self.stdout.write('  Business 3 | builditph      | password123')
        self.stdout.write('  Consumer 1 | juandelacruz   | password123')
        self.stdout.write('  Consumer 2 | mariasantos    | password123')

    def _make_user(self, username, email, password, account_type, is_staff=False, is_superuser=False):
        if Client.objects.filter(username=username).exists():
            return Client.objects.get(username=username)
        user = Client.objects.create_user(
            username=username,
            email=email,
            password=password,
            account_type=account_type,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )
        return user

    def _dummy_file(self):
        """Return a relative path string for the required terms_conditions field."""
        # Just use a placeholder path — no actual file needed for seeding
        return 'uploads/listings/placeholder.pdf'
