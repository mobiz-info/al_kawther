import datetime
import random

from django.db.models import Q
from django.core.management.base import BaseCommand

from decimal import Decimal

from accounts.models import CustomUser
from client_management.models import CustomerOutstanding, CustomerOutstandingReport, CustomerSupply, CustomerSupplyItems, DialyCustomers, InactiveCustomers, OutstandingAmount
from invoice_management.models import Invoice, InvoiceDailyCollection, InvoiceItems
from sales_management.models import Receipt

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        outstanding_invoice_nos = CustomerOutstanding.objects.all().values_list("invoice_no")
        supplies = CustomerSupply.objects.exclude(invoice_no__in=outstanding_invoice_nos)
        
        for supply in supplies:
            date_part = supply.created_date.strftime('%Y%m%d')
            if supply.customer.sales_type == "CASH" or supply.customer.sales_type == "CREDIT" :
                if supply.amount_recieved < supply.subtotal:
                    balance_amount = supply.subtotal - supply.amount_recieved
                    
                    customer_outstanding_amount = CustomerOutstanding.objects.create(
                        product_type="amount",
                        created_by=supply.created_by,
                        customer=supply.customer,
                        created_date=supply.created_date
                    )

                    outstanding_amount = OutstandingAmount.objects.create(
                        amount=balance_amount,
                        customer_outstanding=customer_outstanding_amount,
                    )
                    outstanding_instance = {}

                    try:
                        outstanding_instance=CustomerOutstandingReport.objects.get(customer=supply.customer,product_type="amount")
                        outstanding_instance.value += Decimal(outstanding_amount.amount)
                        outstanding_instance.save()
                    except:
                        outstanding_instance = CustomerOutstandingReport.objects.create(
                            product_type='amount',
                            value=outstanding_amount.amount,
                            customer=outstanding_amount.customer_outstanding.customer
                        )
                        
                elif supply.amount_recieved > supply.subtotal:
                    balance_amount = supply.amount_recieved - supply.subtotal
                    
                    customer_outstanding_amount = CustomerOutstanding.objects.create(
                        product_type="amount",
                        created_by=supply.created_by,
                        customer=supply.customer,
                    )

                    outstanding_amount = OutstandingAmount.objects.create(
                        amount=balance_amount,
                        customer_outstanding=customer_outstanding_amount,
                    )
                    
                    outstanding_instance=CustomerOutstandingReport.objects.get(customer=supply.customer,product_type="amount")
                    outstanding_instance.value -= Decimal(balance_amount)
                    outstanding_instance.save()
                    
                customer_outstanding_amount.invoice_no = supply.invoice_no
                customer_outstanding_amount.save()
            
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {supply.invoice_no}'))
            
        self.stdout.write(self.style.SUCCESS(f'Successfully updated all supplies are updated'))
