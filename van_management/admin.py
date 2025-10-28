from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Van)
admin.site.register(Van_Routes)
admin.site.register(VanStock)
admin.site.register(VanProductItems)
admin.site.register(VanCouponItems)

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('date_created','expense_date','expence_type','amount')
admin.site.register(Expense,ExpenseAdmin)

class OffloadRequestAdmin(admin.ModelAdmin):
    list_display = ('created_date','van','salesman')
admin.site.register(OffloadRequest,OffloadRequestAdmin)

class OffloadRequestItemsAdmin(admin.ModelAdmin):
    list_display = ('quantity','offloaded_quantity','stock_type','product','offload_request')
admin.site.register(OffloadRequestItems,OffloadRequestItemsAdmin)

class OffloadAdmin(admin.ModelAdmin):
    list_display = ('created_date','van','product','quantity','stock_type')
admin.site.register(Offload,OffloadAdmin)

class VanProductStockAdmin(admin.ModelAdmin):
    list_display = ('product','van','created_date','opening_count','change_count','damage_count','empty_can_count','stock','return_count','requested_count','sold_count','closing_count')
admin.site.register(VanProductStock,VanProductStockAdmin)
class VanCouponStockAdmin(admin.ModelAdmin):
    list_display = ('van','coupon','created_date','opening_count','change_count','damage_count','stock','return_count','requested_count','sold_count','closing_count')
admin.site.register(VanCouponStock,VanCouponStockAdmin)

class BottleCountAdmin(admin.ModelAdmin):
    list_display = ('created_date','van','opening_stock','custody_issue','custody_return','qty_added','qty_deducted','closing_stock')
admin.site.register(BottleCount,BottleCountAdmin)