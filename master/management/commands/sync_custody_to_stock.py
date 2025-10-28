from django.core.management.base import BaseCommand

from client_management.models import CustodyCustomItems, CustomerCustodyStock


class Command(BaseCommand):
    help = "Sync CustodyCustomItems into CustomerCustodyStock"

    def handle(self, *args, **options):
        items = CustodyCustomItems.objects.filter(custody_custom__customer__routes__route_name__in=["SL","DM"]).select_related("custody_custom", "product")

        updated, created_count = 0, 0

        for item in items:
            custody = item.custody_custom
            if not custody or not item.product:
                continue

            customer_instance = custody.customer
            product_instance = item.product

            agreement_no = custody.agreement_no or ""
            deposit_type = custody.deposit_type or ""
            reference_no = custody.reference_no or ""
            serialnumber = str(item.serialnumber or "")
            quantity = item.quantity or 0
            amount = item.amount or 0
            can_deposite_chrge = item.can_deposite_chrge or 0
            five_gallon_water_charge = item.five_gallon_water_charge or 0
            amount_collected = custody.amount_collected or 0

            stock_instance, created = CustomerCustodyStock.objects.get_or_create(
                customer=customer_instance,
                product=product_instance,
                defaults={
                    "agreement_no": agreement_no,
                    "deposit_type": deposit_type,
                    "reference_no": reference_no,
                    "quantity": quantity,
                    "serialnumber": serialnumber,
                    "amount": amount,
                    "can_deposite_chrge": can_deposite_chrge,
                    "five_gallon_water_charge": five_gallon_water_charge,
                    "amount_collected": amount_collected,
                },
            )

            if created:
                created_count += 1
            else:
                stock_instance.quantity += quantity
                stock_instance.serialnumber = (
                    (stock_instance.serialnumber + "," + serialnumber)
                    if stock_instance.serialnumber and serialnumber
                    else stock_instance.serialnumber or serialnumber
                )
                stock_instance.agreement_no = (
                    (stock_instance.agreement_no + "," + agreement_no)
                    if stock_instance.agreement_no and agreement_no
                    else stock_instance.agreement_no or agreement_no
                )
                stock_instance.amount += amount
                stock_instance.can_deposite_chrge += can_deposite_chrge
                stock_instance.five_gallon_water_charge += five_gallon_water_charge
                stock_instance.amount_collected += amount_collected
                stock_instance.save()
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Sync completed: {created_count} new stocks created, {updated} updated."
            )
        )
