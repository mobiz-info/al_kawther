import uuid
from django.contrib import admin
from . models import *

# Register your models here.
admin.site.register(CollectionPayment)
admin.site.register(CollectionItems)
admin.site.register(CollectionCheque)
admin.site.register(Receipt)