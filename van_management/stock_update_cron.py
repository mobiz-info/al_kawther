from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from . models import VanCouponStock,VanProductStock


def van_stock_update_scheduled_job():
    today = timezone.now().date() 
    yesterday = today - timedelta(days=1)
    
    print(yesterday)
    
    # yesterday_product_stocks = VanProductStock.objects.filter(created_date=yesterday)
    # for yesterday_product_stock in yesterday_product_stocks:
    #     # Separate the lookup and creation logic
    #     today_product_stock = VanProductStock.objects.filter(
    #         product=yesterday_product_stock.product,
    #         van=yesterday_product_stock.van,
    #         created_date=today
    #     ).first()

    #     if today_product_stock:
    #         today_product_stock.opening_count = yesterday_product_stock.closing_count
    #         today_product_stock.stock = yesterday_product_stock.stock
    #         today_product_stock.save()
    #     else:
    #         VanProductStock.objects.create(
    #             product=yesterday_product_stock.product,
    #             van=yesterday_product_stock.van,
    #             created_date=today,
    #             opening_count=yesterday_product_stock.closing_count,
    #             change_count=yesterday_product_stock.change_count,
    #             damage_count=yesterday_product_stock.damage_count,
    #             empty_can_count=yesterday_product_stock.empty_can_count,
    #             return_count=yesterday_product_stock.return_count,
    #             stock=yesterday_product_stock.stock
    #         )

    # # Fetch all VanCouponStock entries for yesterday
    # yesterday_coupon_stocks = VanCouponStock.objects.filter(created_date=yesterday,closing_count__gt=0)

    # for yesterday_coupon_stock in yesterday_coupon_stocks:
    #     # Get or create today's stock entry
    #     today_coupon_stock, created = VanCouponStock.objects.get_or_create(
    #         coupon=yesterday_coupon_stock.coupon,
    #         van=yesterday_coupon_stock.van,
    #         created_date=today,  # Ensure created_date is set to today
    #         defaults={
    #             'opening_count': yesterday_coupon_stock.closing_count,
    #             'stock': yesterday_coupon_stock.stock,
    #         }
    #     )
    #     if not created:
    #         today_coupon_stock.opening_count = yesterday_coupon_stock.closing_count
    #         today_coupon_stock.save()
        
        # if created:
        #     self.stdout.write(self.style.SUCCESS(f'Created new coupon stock entry for {today_coupon_stock.id}'))
        # else:
        #     today_coupon_stock.opening_count = yesterday_stock.closing_count
        #     today_coupon_stock.save()
        #     self.stdout.write(self.style.SUCCESS(f'Updated opening count for {today_coupon_stock.id}'))