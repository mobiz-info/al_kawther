import datetime
import random

from django.db.models import Sum
from django.core.management.base import BaseCommand

from client_management.models import CustodyCustom, CustodyCustomItems, CustomerCustodyStock


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        CustomerCustodyStock.objects.filter(customer__routes__route_name="SL").delete()
        
        custedy_custom_datas = CustodyCustom.objects.filter(customer__routes__route_name="SL")
        
        for custedy_custom_data in custedy_custom_datas:
            custody_items = CustodyCustomItems.objects.filter(custody_custom=custedy_custom_data)
            
            for item in custody_items:
                if CustomerCustodyStock.objects.filter(
                    customer=custedy_custom_data.customer,
                    product=item.product
                ).exists():
                    stock_instance = CustomerCustodyStock.objects.get(
                        customer=custedy_custom_data.customer,
                        product=item.product
                    )

                    # Update quantity
                    stock_instance.quantity += item.quantity

                    # Safely update serialnumber
                    stock_instance.serialnumber = ",".join(
                        filter(None, [stock_instance.serialnumber, item.serialnumber])
                    )

                    # Safely update agreement_no
                    stock_instance.agreement_no = ",".join(
                        filter(None, [stock_instance.agreement_no, custedy_custom_data.agreement_no])
                    )

                    stock_instance.save()
                else:
                    CustomerCustodyStock.objects.create(
                        customer=custedy_custom_data.customer,
                        agreement_no=custedy_custom_data.agreement_no or "",
                        deposit_type=custedy_custom_data.deposit_type,
                        reference_no=custedy_custom_data.reference_no,
                        product=item.product,
                        quantity=item.quantity,
                        serialnumber=item.serialnumber or "",
                        amount=item.amount,
                        can_deposite_chrge=item.can_deposite_chrge,
                        five_gallon_water_charge=item.five_gallon_water_charge,
                        amount_collected=custedy_custom_data.amount_collected
                    )
                
            self.stdout.write(
                self.style.WARNING(f'Successfully updated {custedy_custom_data.customer.custom_id}')
            )
            
        self.stdout.write(self.style.SUCCESS('Successfully updated all'))
