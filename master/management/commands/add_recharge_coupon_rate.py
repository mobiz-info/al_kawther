from django.core.management.base import BaseCommand
from django.utils import timezone

from client_management.models import CustomerCoupon, CustomerCouponItems
from coupon_management.models import NewCoupon
from product.models import ProdutItemMaster


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **kwargs):
        # customer_coupon_instances = CustomerCoupon.objects.all()
        # coupons = NewCoupon.objects.all()
        # for coupon in coupons:
        #     if coupon.coupon_type:
        #         coupon.valuable_leaflets=coupon.coupon_type.valuable_leaflets
        #         coupon.save()
         
        # # for customer_coupon_instance in customer_coupon_instances:
        # items = CustomerCouponItems.objects.exclude(coupon=None)
        # for item in items:
        #     print(item.coupon)
        #     print(item.coupon.coupon_type.coupon_type_name)
        #     print(item.customer_coupon)
        #     coupon_item_name = item.coupon.coupon_type.coupon_type_name
        #     product_item = ProdutItemMaster.objects.get(product_name__iexact=coupon_item_name)
            
        #     item.rate=product_item.rate
        #     item.save()

        #     self.stdout.write(self.style.WARNING(f'{item.customer_coupon.customer.custom_id} - {item.customer_coupon.customer.customer_name} rate updated'))
        self.stdout.write(self.style.SUCCESS('successfull updated all rates.'))


