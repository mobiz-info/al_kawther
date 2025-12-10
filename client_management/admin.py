from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone

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
    search_fields = ('customer__customer_name',)

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

@admin.register(CustomerSupplyItems)
class CustomerSupplyItemsAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'get_custom_id', 
        'customer_supply', 
        'product', 
        'quantity',  
        'amount', 
        'get_created_date',
        'leaf_count'
    )
    list_filter = ('product',)
    search_fields = ('customer_supply__customer__customer_name', 'customer_supply__customer__custom_id')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Optional: show only items from the last 3 days
        three_days_ago = timezone.now() - timedelta(days=3)
        return qs.filter(customer_supply__created_date__gte=three_days_ago)

    # Show customer custom ID
    def get_custom_id(self, obj):
        return obj.customer_supply.customer.custom_id
    get_custom_id.short_description = "Custom ID"
    get_custom_id.admin_order_field = 'customer_supply__customer__custom_id'

    # Show created date from related CustomerSupply
    def get_created_date(self, obj):
        return obj.customer_supply.created_date
    get_created_date.short_description = 'Created Date'
    get_created_date.admin_order_field = 'customer_supply__created_date'

    # Show leaf count from related coupons
    def leaf_count(self, obj):
        from django.db.models import Count
        return obj.customer_supply.customer_supplycoupon_set.aggregate(
            total=Count('leaf')
        )['total']
    leaf_count.short_description = 'Manual Coupon Leaf Count'
    
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
    list_display = ('id','product','quantity','serialnumber','amount')
    
    # def customer(self, obj):
    #     if obj.custody_custom.customer:
    #         return obj.custody_custom.customer.customer_name
    #     else:
    #         return ""
    
    def product(self, obj):
        return obj.product.product_name
admin.site.register(CustodyCustomItems,CustodyCustomItemsAdmin)

@admin.register(CustodyCustom)
class CustodyCustomAdmin(admin.ModelAdmin):
    list_display = (
        'customer',
        'agreement_no',
        'total_amount',
        'deposit_type',
        'reference_no',
        'amount_collected',
        
        'created_by',
        'created_date',
    )
    list_filter = ('deposit_type',  'created_date')
    search_fields = ( 'agreement_no', 'reference_no', 'customer__name')
    date_hierarchy = 'created_date'
    readonly_fields = ( 'created_date', 'modified_date')

    fieldsets = (
        ('Custody Information', {
            'fields': (
                'customer',
                
                'agreement_no',
                'total_amount',
                'deposit_type',
                'reference_no',
                'amount_collected',
                
            )
        }),
        ('Audit Information', {
            'fields': (
                'created_by',
                'created_date',
                'modified_by',
                'modified_date',
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        """Auto-fill created_by and modified_by fields."""
        if not obj.created_by:
            obj.created_by = request.user.username
        obj.modified_by = request.user.username
        super().save_model(request, obj, form, change)

class CustomerCustodyStockAdmin(admin.ModelAdmin):
    list_display = ('id','customer','product','quantity','serialnumber','amount')
    
    def customer(self, obj):
        return obj.customer.customer_name
    
    def product(self, obj):
        return obj.product.product_name
admin.site.register(CustomerCustodyStock,CustomerCustodyStockAdmin)
@admin.register(CustomerReturn)
class CustomerReturnAdmin(admin.ModelAdmin):
    list_display = ( 'customer_name', 'customer_route', 'deposit_type', 'created_date')
    search_fields = ( 'customer__customer_name', 'customer__routes__route_name')
    list_filter = ('deposit_type', 'created_date')

    def customer_name(self, obj):
        return obj.customer.customer_name if obj.customer else "-"
    customer_name.short_description = "Customer"

    def customer_route(self, obj):
        return obj.customer.routes.route_name if obj.customer and obj.customer.routes else "-"
    customer_route.short_description = "Route"


@admin.register(CustomerReturnItems)
class CustomerReturnItemsAdmin(admin.ModelAdmin):
    list_display = ('customer_return_no', 'customer_name', 'route_name', 'product', 'quantity', 'amount')
    search_fields = (
        'customer_return__return_no',          # search by return number
        'customer_return__customer__customer_name',  # search by customer name
        'customer_return__customer__routes__route_name',  # search by route name
    )

    def customer_return_no(self, obj):
        return obj.customer_return.return_no if obj.customer_return else "-"
    customer_return_no.short_description = "Return No"

    def customer_name(self, obj):
        if obj.customer_return and obj.customer_return.customer:
            return obj.customer_return.customer.customer_name
        return "-"
    customer_name.short_description = "Customer"

    def route_name(self, obj):
        if obj.customer_return and obj.customer_return.customer and obj.customer_return.customer.routes:
            return obj.customer_return.customer.routes.route_name
        return "-"
    route_name.short_description = "Route"