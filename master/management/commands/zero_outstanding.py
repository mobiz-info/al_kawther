from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils.timezone import make_aware
from datetime import datetime

from invoice_management.models import Invoice
from client_management.models import CustomerOutstanding, OutstandingAmount


class Command(BaseCommand):
    help = "Fix mismatches: update OutstandingAmount to match Invoice.amount for route S-37"

    def handle(self, *args, **kwargs):

        start_date = make_aware(datetime(2024, 9, 1))
        end_date = make_aware(datetime(2024, 11, 30, 23, 59, 59))

        route = "S-37"

        invoices = Invoice.objects.filter(
            created_date__range=(start_date, end_date),
            customer__routes__route_name=route,
            is_deleted=False
        ).exclude(invoice_no__isnull=True).exclude(invoice_no__exact="")

        updated_count = 0

        for inv in invoices:

            invoice_amount = inv.amout_total or 0
            invoice_no = inv.invoice_no
            customer = inv.customer

            # Get or create outstanding header
            outstanding, created = CustomerOutstanding.objects.get_or_create(
                customer=customer,
                invoice_no=invoice_no,
                product_type="amount",
                defaults={
                    "created_by": "system",
                    "created_date": inv.created_date
                }
            )

            # Sum existing outstanding
            existing_amount = OutstandingAmount.objects.filter(
                customer_outstanding=outstanding
            ).aggregate(total=Sum('amount'))['total'] or 0

            if float(existing_amount) != float(invoice_amount):

                # Remove existing rows
                OutstandingAmount.objects.filter(customer_outstanding=outstanding).delete()

                # Create new correct row
                OutstandingAmount.objects.create(
                    customer_outstanding=outstanding,
                    amount=invoice_amount
                )

                updated_count += 1

                self.stdout.write(
                    f"Updated {invoice_no}: outstanding {existing_amount} → {invoice_amount}"
                )

        self.stdout.write(self.style.SUCCESS(
            f"\nCompleted! Fixed {updated_count} mismatched invoices for route {route}."
        ))
