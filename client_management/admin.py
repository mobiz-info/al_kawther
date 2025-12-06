from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

# Register your models here.
from . models import *

class CustomerCouponStockAdmin(admin.ModelAdmin):
    list_display = ('coupon_type_id', 'coupon_method', 'customer','count')
admin.site.register(CustomerCouponStock,CustomerCouponStockAdmin)

admin.site.register(CustomerCoupon)
admin.site.register(CustomerCouponItems)
admin.site.register(ChequeCouponPayment)

class CustomerOutstandingAdmin(admin.ModelAdmin):
    list_display = ('id','invoice_no','created_by','created_date','product_type','customer')
    ordering = ("-created_date",)
    search_fields = ('invoice_no','customer__custom_id')

    def delete_button(self, obj):
        delete_url = reverse('admin:%s_%s_delete' % (obj._meta.app_label, obj._meta.model_name), args=[obj.id])
        return format_html('<a href="{}" class="button" style="color:red;">Delete</a>', delete_url)

    delete_button.short_description = 'Delete'
    delete_button.allow_tags = True

admin.site.register(CustomerOutstanding,CustomerOutstandingAdmin)

admin.site.register(OutstandingProduct)

class CustomerOutstandingAmountAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'invoice_no',
        'created_by',
        'created_date',
        'customer',
        'amount'
    )
    ordering = ("-customer_outstanding__created_date",)
    
    def invoice_no(self, obj):
        return obj.customer_outstanding.invoice_no
    invoice_no.admin_order_field = 'customer_outstanding__invoice_no'
    invoice_no.short_description = 'Invoice No'

    def created_by(self, obj):
        return obj.customer_outstanding.created_by
    created_by.admin_order_field = 'customer_outstanding__created_by'
    created_by.short_description = 'Created By'

    def created_date(self, obj):
        return obj.customer_outstanding.created_date
    created_date.admin_order_field = 'customer_outstanding__created_date'
    created_date.short_description = 'Created Date'

    def customer(self, obj):
        return obj.customer_outstanding.customer
    customer.admin_order_field = 'customer_outstanding__customer'
    customer.short_description = 'Customer'

admin.site.register(OutstandingAmount, CustomerOutstandingAmountAdmin)

admin.site.register(OutstandingCoupon)
class CustomerOutstandingReportAdmin(admin.ModelAdmin):
    list_display = ('id','product_type','customer','value')
admin.site.register(CustomerOutstandingReport,CustomerOutstandingReportAdmin)

class CustomerSupplyAdmin(admin.ModelAdmin):
    list_display = (
        'id','created_date','customer', 'salesman', 'grand_total', 'allocate_bottle_to_pending',
        'allocate_bottle_to_custody', 'allocate_bottle_to_paid', 'discount',
        'net_payable', 'vat', 'subtotal', 'amount_recieved','outstanding_amount_added',
        'outstanding_coupon_added','outstanding_bottle_added','van_stock_added','van_foc_added',
        'van_emptycan_added','custody_added'
    )
    list_filter = ('salesman',)  # Other filters if needed
    list_filter = ('customer__routes',)  # Other filters if needed
    search_fields = ('customer__customer_name',)  # Search by customer name (ForeignKey field)

admin.site.register(CustomerSupply, CustomerSupplyAdmin)

admin.site.register(CustomerSupplyItems)
admin.site.register(CustomerSupplyStock)
admin.site.register(CustomerCart)
admin.site.register(CustomerCartItems)
admin.site.register(CustomerOtherProductChargesChanges)
admin.site.register(CustomerOtherProductCharges)

class DialyCustomersAdmin(admin.ModelAdmin):
    list_display = ('id','date','customer','route','qty','is_emergency','is_supply')
    ordering = ("-date",)
    
    def customer(self, obj):
        return obj.customer.customer_name
    
    def route(self, obj):
        return obj.route.route_name
admin.site.register(DialyCustomers,DialyCustomersAdmin)

class CustodyCustomItemsAdmin(admin.ModelAdmin):
    list_display = ('id','customer','product','quantity','serialnumber','amount')
    
    def customer(self, obj):
        return obj.custody_custom.customer.customer_name
    
    def product(self, obj):
        return obj.product.product_name
admin.site.register(CustodyCustomItems,CustodyCustomItemsAdmin)

class CustomerCustodyStockAdmin(admin.ModelAdmin):
    list_display = ('id','customer','product','quantity','serialnumber','amount')
    
    def customer(self, obj):
        return obj.customer.customer_name
    
    def product(self, obj):
        return obj.product.product_name
admin.site.register(CustomerCustodyStock,CustomerCustodyStockAdmin)