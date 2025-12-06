import uuid
from django.contrib import admin
from . models import *

# Register your models here.
class CollectionPaymentAdmin(admin.ModelAdmin):
    # Show all fields dynamically
    list_display = [field.name for field in CollectionPayment._meta.get_fields() if not field.many_to_many and not field.one_to_many]

    # Searchable fields: CharField/TextField + related fields
    search_fields = [
        'receipt_number',
        'customer__name',    # Assuming Customers has 'name' field
        'salesman__username',# Assuming CustomUser has 'username' field
        'payment_method'
    ]

    # Optional: Add filters for ForeignKeys or choices
    list_filter = ('payment_method', 'salesman', 'created_date')

# Admin for CollectionItems
class CollectionItemsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CollectionItems._meta.get_fields() if not field.many_to_many and not field.one_to_many]

    search_fields = [
        'invoice__invoice_number',    # Assuming Invoice has invoice_number field
        'collection_payment__receipt_number',
        'collection_payment__customer__name'
    ]

    list_filter = ('collection_payment__payment_method',)

admin.site.register(CollectionPayment, CollectionPaymentAdmin)
admin.site.register(CollectionItems, CollectionItemsAdmin)

admin.site.register(CollectionCheque)
admin.site.register(Receipt)
