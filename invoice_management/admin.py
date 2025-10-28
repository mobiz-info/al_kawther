from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import *

# Register your models here.
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'customer', 'reference_no', 'invoice_no', 'invoice_type', 
        'invoice_status', 'created_date', 'net_taxable', 'vat', 
        'discount', 'amout_total', 'amout_recieved', 'delete_button'
    )
    ordering = ("-created_date",)
    search_fields = ('invoice_no',)

    def delete_button(self, obj):
        delete_url = reverse('admin:%s_%s_delete' % (obj._meta.app_label, obj._meta.model_name), args=[obj.id])
        return format_html('<a href="{}" class="button" style="color:red;">Delete</a>', delete_url)

    delete_button.short_description = 'Delete'
    delete_button.allow_tags = True

admin.site.register(Invoice, InvoiceAdmin)

class InvoiceItemsAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'product_items', 'qty', 'rate')
    search_fields = ('invoice__invoice_no',)  # Enable searching by related invoice number
admin.site.register(InvoiceItems, InvoiceItemsAdmin)

admin.site.register(SuspenseCollection)
