from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from client_management.models import CustomerCouponItems
from coupon_management.models import CouponStock


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        customer_coupon_ids = CustomerCouponItems.objects.all().values_list("coupon__coupon_id")
        CouponStock.objects.filter(couponbook__coupon_id__in=customer_coupon_ids).update(coupon_stock="customer")
        
        self.stdout.write(self.style.SUCCESS('Stock update process completed.'))
