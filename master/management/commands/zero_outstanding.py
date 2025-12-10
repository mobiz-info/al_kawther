from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils.timezone import make_aware
from datetime import datetime

from invoice_management.models import Invoice
from client_management.models import CustomerOutstanding, OutstandingAmount


class Command(BaseCommand):
    help = "Check invoice vs outstanding mismatches for route S-37"

    def handle(self, *args, **kwargs):

        start_date = make_aware(datetime(2024, 9, 1))
        end_date = make_aware(datetime(2024, 11, 30, 23, 59, 59))

        invoices = Invoice.objects.filter(
            created_date__range=(start_date, end_date),
            customer__routes__route_name="S-37",
            is_deleted=False
        )

        mismatches = []

        for inv in invoices:

            invoice_amount = inv.amout_total or 0
            invoice_no = inv.invoice_no
            customer = inv.customer

            outstanding = CustomerOutstanding.objects.filter(
                customer=customer,
                invoice_no=invoice_no,
                product_type="amount"
            ).first()

            if not outstanding:
                mismatches.append({
                    "invoice_no": invoice_no,
                    "customer": str(customer),
                    "invoice_amount": float(invoice_amount),
                    "outstanding_amount": 0,
                    "status": "NO OUTSTANDING ENTRY"
                })
                continue

            outstanding_amount = OutstandingAmount.objects.filter(
                customer_outstanding=outstanding
            ).aggregate(total=Sum('amount'))['total'] or 0

            # only mismatches
            if float(invoice_amount) != float(outstanding_amount):
                mismatches.append({
                    "invoice_no": invoice_no,
                    "customer": str(customer),
                    "invoice_amount": float(invoice_amount),
                    "outstanding_amount": float(outstanding_amount),
                    "status": "NOT MATCH"
                })

        # Print results
        if mismatches:
            self.stdout.write("\nMISMATCHED INVOICES:\n")
            for r in mismatches:
                self.stdout.write(str(r))
        else:
            self.stdout.write("All invoice amounts match outstanding amounts!")
