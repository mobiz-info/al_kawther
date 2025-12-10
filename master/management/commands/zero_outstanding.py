from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils.timezone import make_aware
from datetime import datetime

from invoice_management.models import Invoice
from client_management.models import CustomerOutstanding, OutstandingAmount


class Command(BaseCommand):
    help = "Update outstanding amounts ONLY when invoice_no matches exactly (route S-37)."

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

            # get ONLY the outstanding entry with SAME invoice_no
            outstanding = CustomerOutstanding.objects.filter(
                customer=customer,
                invoice_no=invoice_no,   # **** STRICT MATCH CHECK ****
                product_type="amount"
            ).first()

            # If outstanding does NOT exist → DO NOTHING
            if not outstanding:
                continue

            # Sum its outstanding amounts
            existing_total = OutstandingAmount.objects.filter(
                customer_outstanding=outstanding
            ).aggregate(total=Sum('amount'))['total'] or 0

            # Update only mismatches
            if float(existing_total) != float(invoice_amount):

                # Delete old amounts
                OutstandingAmount.objects.filter(customer_outstanding=outstanding).delete()

                # Insert correct updated row
                OutstandingAmount.objects.create(
                    customer_outstanding=outstanding,
                    amount=invoice_amount,
                )

                updated_count += 1
                self.stdout.write(
                    f"UPDATED: Invoice {invoice_no} | Old: {existing_total} → New: {invoice_amount}"
                )

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Updated {updated_count} invoices where invoice_no matched and amount mismatched."
        ))