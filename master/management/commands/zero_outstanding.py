import os
from django.core.management.base import BaseCommand
from django.db.models import Sum
from openpyxl import Workbook
from accounts.models import Customers
from client_management.models import CustomerOutstanding


class Command(BaseCommand):
    help = "Export all customers whose total outstanding amount = 0 into Excel"

    def handle(self, *args, **kwargs):
        self.stdout.write("Calculating customers with zero outstanding amount...")

        wb = Workbook()
        ws = wb.active
        ws.title = "Zero Outstanding Customers"

        # Header row
        ws.append(["Customer ID", "Customer Name", "Total Outstanding"])

        customers = Customers.objects.all()
        zero_count = 0

        for customer in customers:
            total_amount = CustomerOutstanding.objects.filter(
                customer=customer
            ).aggregate(total=Sum("total_amount"))["total"] or 0

            if total_amount == 0:
                ws.append([customer.custom_id, customer.customer_name, 0])
                zero_count += 1

        filename = "zero_outstanding_customers.xlsx"
        wb.save(filename)

        self.stdout.write(self.style.SUCCESS(
            f"Completed. {zero_count} customers found with zero outstanding amount."
        ))
        self.stdout.write(self.style.SUCCESS(f"Excel saved as: {filename}"))
