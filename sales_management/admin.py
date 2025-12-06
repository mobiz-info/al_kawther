import uuid
from django.contrib import admin
from . models import *

# Register your models here.
class CollectionPaymentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CollectionPayment._meta.get_fields()]

# Dynamically get all fields for CollectionItems
class CollectionItemsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CollectionItems._meta.get_fields()]

admin.site.register(CollectionPayment, CollectionPaymentAdmin)
admin.site.register(CollectionItems, CollectionItemsAdmin)
admin.site.register(CollectionCheque)
admin.site.register(Receipt)
