import uuid
from django.db.models import Sum
from django.core.management.base import BaseCommand
from django.utils import timezone

from client_management.models import Customers, CustomerReturnItems
from client_management.models import CustodyCustom, CustodyCustomItems
from product.models import ProdutItemMaster

class Command(BaseCommand):
    help = "Update no_of_bottles_required for DM route customers and save custody items"

    def handle(self, *args, **kwargs):
        # Fetch DM route customers
        dm_customers = Customers.objects.filter(routes__route_name="SL", is_deleted=False, is_cancelled=False)

        updated_count = 0

        for customer in dm_customers:
            # --- Calculate custody quantity ---
            custody_quantity = CustodyCustomItems.objects.filter(
                custody_custom__customer=customer, product__product_name="5 Gallon"
            ).aggregate(total=Sum("quantity"))["total"] or 0

            custody_return = CustomerReturnItems.objects.filter(
                customer_return__customer=customer, product__product_name="5 Gallon"
            ).aggregate(total=Sum("quantity"))["total"] or 0

            custody_qty = abs(custody_quantity - custody_return)

            # --- Update customer's no_of_bottles_required ---
            if customer.no_of_bottles_required != custody_qty:
                customer.no_of_bottles_required = custody_qty
                customer.save(update_fields=["no_of_bottles_required"])
                updated_count += 1
                self.stdout.write(self.style.WARNING(
                    f"Updated {customer.custom_id} → no_of_bottles_required: {custody_qty}"
                ))

            # --- Create or update CustodyCustom and CustodyCustomItems ---
            custody_custom = CustodyCustom.objects.filter(customer=customer).order_by('-created_date').first()

            if not custody_custom:
                custody_custom = CustodyCustom.objects.create(
                    customer=customer,
                    agreement_no=f"AG-{uuid.uuid4().hex[:6].upper()}",
                    reference_no=f"REF-{uuid.uuid4().hex[:6].upper()}",
                    deposit_type="Default",
                    amount_collected=0,
                    created_by="system",
                )

            # --- CustodyCustomItems for 5 Gallon ---
            product_5g = ProdutItemMaster.objects.get(product_name="5 Gallon")
            custody_item, item_created = CustodyCustomItems.objects.get_or_create(
                custody_custom=custody_custom,
                product=product_5g,
                defaults={
                    "quantity": custody_qty,
                    "amount": 0,
                    "can_deposite_chrge": 0,
                    "five_gallon_water_charge": 0,
                }
            )

            if not item_created:
                custody_item.quantity = custody_qty
                custody_item.save(update_fields=["quantity"])
                self.stdout.write(self.style.SUCCESS(
                    f"Updated CustodyCustomItems for {customer.custom_id} → quantity: {custody_qty}"
                ))

        self.stdout.write(self.style.SUCCESS(f"Successfully updated {updated_count} DM customers"))