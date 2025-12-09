import os
import django
import openpyxl


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from client_management.models import OutstandingAmount   


def export_zero_outstanding_s3():
    print("Generating Excel for Route S-3 (amount = 0)...")

   
    data = (
        OutstandingAmount.objects
        .filter(amount=0)
        .select_related("customer_outstanding__customer")
        .filter(customer_outstanding__customer__routes__route_name="S-15")
    )

    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "S-15 Zero Outstanding"

    
    ws.append(["Customer ID", "Customer Name", "Invoice No", "Route", "Amount"])

    
    for item in data:
        customer = item.customer_outstanding.customer
        route_name = customer.routes.route_name if customer and customer.routes else ""

        ws.append([
            customer.custom_id if customer else "",
            customer.customer_name if customer else "",
            item.customer_outstanding.invoice_no,
            route_name,
            float(item.amount),
        ])

    
    file_name = "zero_outstanding_s15.xlsx"
    wb.save(file_name)

    print(f"Excel Created Successfully: {file_name}")


if __name__ == "__main__":
    export_zero_outstanding_s3()