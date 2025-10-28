import datetime
from datetime import date as datetime
from django import template
from django.db.models import Q, Sum

from accounts.models import Customers
from master.functions import get_next_visit_date
from client_management.models import *
register = template.Library()

@register.simple_tag
def get_next_visit_day(customer_pk):
    customer = Customers.objects.get(pk=customer_pk)
    if not customer.visit_schedule is None:
        next_visit_date = get_next_visit_date(customer.visit_schedule)
        # customer.next_visit_date = next_visit_date
        return next_visit_date
    else:
      return "-"

# @register.simple_tag
# def bottle_stock(customer_pk):
#     customer = Customers.objects.get(pk=customer_pk)
#     custody_count = 0

#         custody_count = custody_stock.first().quantity 

#     total_supplied_count = CustomerSupplyItems.objects.filter(customer_supply__customer=customer).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
#     total_empty_collected = CustomerSupply.objects.filter(customer=customer).aggregate(total_quantity=Sum('collected_empty_bottle'))['total_quantity'] or 0

#     total_bottle_count = custody_count + total_supplied_count - total_empty_collected

#     return total_bottle_count
@register.simple_tag
def bottle_stock(customer_pk):
    customer_supply_items = CustomerSupplyItems.objects.filter(customer_supply__customer__pk=customer_pk, product__product_name="5 Gallon")
    
    bottle_supplied = customer_supply_items.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    bottle_to_custody = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__allocate_bottle_to_custody'))['total_quantity'] or 0
    bottle_to_paid = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__allocate_bottle_to_paid'))['total_quantity'] or 0
    
    foc_supply = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__allocate_bottle_to_free'))['total_quantity'] or 0
    empty_bottle_collected = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__collected_empty_bottle'))['total_quantity'] or 0
    
    custody_quantity = CustodyCustomItems.objects.filter(custody_custom__customer__pk=customer_pk, product__product_name="5 Gallon").aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    custody_return = CustomerReturnItems.objects.filter(customer_return__customer__pk=customer_pk, product__product_name="5 Gallon").aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    
    supply_qty = abs(((bottle_supplied - bottle_to_custody - bottle_to_paid) + foc_supply) - empty_bottle_collected)
    custody_qty = abs(custody_quantity - custody_return)

    return supply_qty + custody_qty

@register.simple_tag
def dispenser_stock(customer_pk):
    customer_supply_items = CustomerSupplyItems.objects.filter(customer_supply__customer__pk=customer_pk, product__product_name="Dispenser")
    
    supplied = customer_supply_items.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    custody = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__allocate_bottle_to_custody'))['total_quantity'] or 0
    
    custody_quantity = CustodyCustomItems.objects.filter(custody_custom__customer__pk=customer_pk, product__product_name="Dispenser").aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    custody_return = CustomerReturnItems.objects.filter(customer_return__customer__pk=customer_pk, product__product_name="Dispenser").aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    
    supply_qty = abs(supplied - custody)
    custody_qty = abs(custody_quantity - custody_return)

    return supply_qty + custody_qty

@register.simple_tag
def hot_cool_stock(customer_pk):
    customer_supply_items = CustomerSupplyItems.objects.filter(customer_supply__customer__pk=customer_pk, product__product_name="Hot and Cool")
    
    supplied = customer_supply_items.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    custody = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__allocate_bottle_to_custody'))['total_quantity'] or 0
    
    custody_quantity = CustodyCustomItems.objects.filter(custody_custom__customer__pk=customer_pk, product__product_name="Hot and Cool").aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    custody_return = CustomerReturnItems.objects.filter(customer_return__customer__pk=customer_pk, product__product_name="Hot and Cool").aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    
    supply_qty = abs(supplied - custody)
    custody_qty = abs(custody_quantity - custody_return)

    return supply_qty + custody_qty

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.simple_tag
def other_product_rate(customer_pk,product_id):
    rate = ProdutItemMaster.objects.get(pk=product_id).rate
    if (rate_change_instances:=CustomerOtherProductCharges.objects.filter(product_item__pk=product_id,customer__pk=customer_pk)).exists():
        rate = rate_change_instances.first().current_rate
    return rate


