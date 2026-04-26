from decimal import Decimal
from itertools import cycle

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from authentication.models import BusinessProfile, Client
from purchase_requests.models import Offer, Participation, PurchaseRequest


PDF_BYTES = (
    b"%PDF-1.4\n"
    b"1 0 obj<<>>endobj\n"
    b"2 0 obj<< /Type /Catalog /Pages 3 0 R >>endobj\n"
    b"3 0 obj<< /Type /Pages /Kids [4 0 R] /Count 1 >>endobj\n"
    b"4 0 obj<< /Type /Page /Parent 3 0 R /MediaBox [0 0 300 144] "
    b"/Contents 5 0 R /Resources << >> >>endobj\n"
    b"5 0 obj<< /Length 44 >>stream\n"
    b"BT /F1 12 Tf 36 100 Td (Demo RFQ Document) Tj ET\n"
    b"endstream\nendobj\n"
    b"xref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n"
    b"0000000031 00000 n \n0000000080 00000 n \n0000000139 00000 n \n"
    b"0000000240 00000 n \ntrailer<< /Root 2 0 R /Size 6 >>\n"
    b"startxref\n334\n%%EOF\n"
)


class Command(BaseCommand):
    help = "Seed demo purchase requests, participations, and offers for local testing."

    DEMO_USERS = [
        {
            "username": "demo_buyer",
            "email": "demo_buyer@example.com",
            "business_name": "Demo Buyer Supply Co.",
            "tin": "900000001",
        },
        {
            "username": "demo_seller1",
            "email": "demo_seller1@example.com",
            "business_name": "Demo Seller Logistics",
            "tin": "900000002",
        },
        {
            "username": "demo_seller2",
            "email": "demo_seller2@example.com",
            "business_name": "Demo Seller Tech",
            "tin": "900000003",
        },
    ]

    SAMPLE_REQUESTS = [
        {
            "title": "[Demo] Office Chairs for New Branch",
            "description": "Need ergonomic office chairs for a newly opened branch office.",
            "category": "goods",
            "area_of_delivery": "Quezon City",
            "budget": Decimal("125000.00"),
            "deadline_days": 14,
            "status": "open",
            "offers": ["submitted", "submitted"],
        },
        {
            "title": "[Demo] Managed IT Support Renewal",
            "description": "Looking for a monthly managed IT support package for 50 staff.",
            "category": "it",
            "area_of_delivery": "Makati",
            "budget": Decimal("85000.00"),
            "deadline_days": 9,
            "status": "open",
            "offers": ["submitted"],
        },
        {
            "title": "[Demo] Delivery Vans Lease",
            "description": "Seeking two leased delivery vans with maintenance included.",
            "category": "equipment",
            "area_of_delivery": "Pasig",
            "budget": Decimal("240000.00"),
            "deadline_days": 18,
            "status": "open",
            "offers": [],
        },
        {
            "title": "[Demo] Warehouse Roof Repair",
            "description": "Roof leak repair and reinforcement for a medium-sized warehouse.",
            "category": "construction",
            "area_of_delivery": "Caloocan",
            "budget": Decimal("315000.00"),
            "deadline_days": -2,
            "status": "closed",
            "offers": ["submitted"],
        },
        {
            "title": "[Demo] Pantry Supplies Restock",
            "description": "Quarterly restock for pantry beverages, snacks, and disposable cups.",
            "category": "goods",
            "area_of_delivery": "Taguig",
            "budget": Decimal("48000.00"),
            "deadline_days": 11,
            "status": "open",
            "offers": ["submitted", "submitted"],
        },
        {
            "title": "[Demo] Fiber Internet Backup Line",
            "description": "Need an ISP backup line with business-grade SLA and installation.",
            "category": "it",
            "area_of_delivery": "Mandaluyong",
            "budget": Decimal("62000.00"),
            "deadline_days": 7,
            "status": "open",
            "offers": ["submitted"],
        },
        {
            "title": "[Demo] Company Shuttle Service",
            "description": "Requesting transport service for employees during peak hours.",
            "category": "services",
            "area_of_delivery": "Pasay",
            "budget": Decimal("178000.00"),
            "deadline_days": 16,
            "status": "open",
            "offers": ["submitted"],
        },
        {
            "title": "[Demo] CCTV Expansion Project",
            "description": "Expansion of CCTV coverage for office entrances and loading docks.",
            "category": "equipment",
            "area_of_delivery": "Paranaque",
            "budget": Decimal("96000.00"),
            "deadline_days": -1,
            "status": "closed",
            "offers": ["submitted", "submitted"],
        },
        {
            "title": "[Demo] Laptop Procurement Batch 1",
            "description": "Purchase of 12 work laptops with docking stations and bags.",
            "category": "it",
            "area_of_delivery": "Manila",
            "budget": Decimal("540000.00"),
            "deadline_days": 5,
            "status": "completed",
            "offers": ["accepted", "rejected"],
        },
        {
            "title": "[Demo] Janitorial Services Contract",
            "description": "Outsource janitorial services for a six-month engagement.",
            "category": "services",
            "area_of_delivery": "San Juan",
            "budget": Decimal("132000.00"),
            "deadline_days": 13,
            "status": "open",
            "offers": [],
        },
        {
            "title": "[Demo] Loading Bay Paint Rework",
            "description": "Surface prep and repainting of the loading bay lane markings.",
            "category": "construction",
            "area_of_delivery": "Valenzuela",
            "budget": Decimal("41000.00"),
            "deadline_days": 3,
            "status": "cancelled",
            "offers": [],
        },
        {
            "title": "[Demo] Packaging Materials Supply",
            "description": "Bulk order of corrugated boxes, tape, and protective fillers.",
            "category": "goods",
            "area_of_delivery": "Marikina",
            "budget": Decimal("73000.00"),
            "deadline_days": 12,
            "status": "open",
            "offers": ["submitted"],
        },
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=len(self.SAMPLE_REQUESTS),
            help="Number of sample purchase requests to create.",
        )

    def handle(self, *args, **options):
        requested_count = max(1, options["count"])

        businesses = list(BusinessProfile.objects.select_related("client").order_by("client__id"))
        businesses.extend(self._ensure_demo_businesses())

        # Approve all business profiles so the seeded requests show up in browse flows.
        BusinessProfile.objects.exclude(status="approved").update(status="approved")
        businesses = list(BusinessProfile.objects.select_related("client").order_by("client__id"))

        if len(businesses) < 2:
            self.stdout.write(self.style.ERROR("Need at least two business accounts to seed offer flows."))
            return

        created_requests = 0
        created_offers = 0
        created_participations = 0
        buyer_cycle = cycle(businesses)

        for index, sample in enumerate(self.SAMPLE_REQUESTS[:requested_count], start=1):
            buyer_profile = next(buyer_cycle)
            title = sample["title"]
            pr, pr_created = PurchaseRequest.objects.get_or_create(
                title=title,
                buyer=buyer_profile.client,
                defaults={
                    "description": sample["description"],
                    "category": sample["category"],
                    "area_of_delivery": sample["area_of_delivery"],
                    "budget": sample["budget"],
                    "closing_deadline": timezone.now() + timezone.timedelta(days=sample["deadline_days"]),
                    "status": sample["status"],
                },
            )

            if pr_created or not pr.rfq_file:
                pr.rfq_file.save(
                    f"demo-rfq-{index}.pdf",
                    ContentFile(PDF_BYTES),
                    save=False,
                )

            pr.description = sample["description"]
            pr.category = sample["category"]
            pr.area_of_delivery = sample["area_of_delivery"]
            pr.budget = sample["budget"]
            pr.closing_deadline = timezone.now() + timezone.timedelta(days=sample["deadline_days"])
            pr.status = sample["status"]
            pr.save()

            if pr_created:
                created_requests += 1

            seller_profiles = [profile for profile in businesses if profile.client_id != buyer_profile.client_id]
            for offer_index, offer_status in enumerate(sample["offers"], start=1):
                seller_profile = seller_profiles[(offer_index - 1) % len(seller_profiles)]
                participation, participation_created = Participation.objects.get_or_create(
                    seller=seller_profile.client,
                    purchase_request=pr,
                    defaults={"is_participating": True},
                )
                if participation_created:
                    created_participations += 1
                elif not participation.is_participating:
                    participation.is_participating = True
                    participation.save(update_fields=["is_participating"])

                offer, offer_created = Offer.objects.get_or_create(
                    seller=seller_profile.client,
                    purchase_request=pr,
                    defaults={"status": offer_status},
                )
                if offer_created or not offer.offer_file:
                    offer.offer_file.save(
                        f"demo-offer-{index}-{offer_index}.pdf",
                        ContentFile(PDF_BYTES),
                        save=False,
                    )
                offer.status = offer_status
                offer.save()
                if offer_created:
                    created_offers += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded purchase request demo data. Created {created_requests} requests, "
                f"{created_participations} participations, and {created_offers} offers."
            )
        )
        self.stdout.write("Demo business logins available with password: demo12345")
        self.stdout.write(" - demo_buyer")
        self.stdout.write(" - demo_seller1")
        self.stdout.write(" - demo_seller2")

    def _ensure_demo_businesses(self):
        created_profiles = []
        for index, user_data in enumerate(self.DEMO_USERS, start=1):
            client, created = Client.objects.get_or_create(
                username=user_data["username"],
                defaults={
                    "email": user_data["email"],
                    "account_type": "business",
                    "contact_number": f"0917000000{index}",
                },
            )
            if created:
                client.set_password("demo12345")
                client.save(update_fields=["password"])

            profile, _ = BusinessProfile.objects.get_or_create(
                client=client,
                defaults={
                    "business_name": user_data["business_name"],
                    "business_address": "123 Demo Street, Metro Manila",
                    "tin": user_data["tin"],
                    "business_type": "trading",
                    "rep_name": "Demo Representative",
                    "rep_position": "Operations Manager",
                    "rep_contact": f"0918000000{index}",
                    "status": "approved",
                },
            )
            created_profiles.append(profile)
        return created_profiles
