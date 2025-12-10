from django.db.models import Sum
from django.utils.timezone import make_aware
from datetime import datetime
from invoice_management.models import Invoice
from client_management.models import CustomerOutstanding, OutstandingAmount

start_date = make_aware(datetime(2024, 9, 1))
end_date = make_aware(datetime(2024, 11, 30, 23, 59, 59))

# Filter invoices for route S-37
invoices = Invoice.objects.filter(
    created_date__range=(start_date, end_date),
    customer__route="S-37",            # <-- CHANGE IF FIELD IS DIFFERENT
    is_deleted=False
).exclude(invoice_no__isnull=True).exclude(invoice_no__exact="")

results = []

for inv in invoices:

    invoice_amount = inv.amout_total or 0
    invoice_no = inv.invoice_no
    customer = inv.customer

    # Find matching outstanding amount entry
    outstanding = CustomerOutstanding.objects.filter(
        customer=customer,
        invoice_no=invoice_no,
        product_type="amount"
    ).first()

    if not outstanding:
        # Show only mismatches → outstanding missing is a mismatch
        results.append({
            "invoice_no": invoice_no,
            "customer": str(customer),
            "invoice_amount": float(invoice_amount),
            "outstanding_amount": 0,
            "status": "NO OUTSTANDING ENTRY"
        })
        continue

    # Calculate outstanding amount
    outstanding_amount = OutstandingAmount.objects.filter(
        customer_outstanding=outstanding
    ).aggregate(total=Sum('amount'))['total'] or 0

    # We only want mismatches
    if float(invoice_amount) != float(outstanding_amount):
        results.append({
            "invoice_no": invoice_no,
            "customer": str(customer),
            "invoice_amount": float(invoice_amount),
            "outstanding_amount": float(outstanding_amount),
            "status": "NOT MATCH"
        })

# Print mismatches
for r in results:
    print(r)
