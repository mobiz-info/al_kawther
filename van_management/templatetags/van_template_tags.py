from datetime import datetime, timedelta
from decimal import Decimal

from django import template
from django.db.models import Sum, Q, F, ExpressionWrapper, IntegerField, Value, Case, When
from django.db.models.functions import Coalesce

from accounts.models import CustomUser
from client_management.models import CustodyCustom, CustodyCustomItems, CustomerCouponItems, CustomerReturnItems, CustomerSupply, CustomerSupplyItems
from master.models import CategoryMaster
from product.models import Staff_IssueOrders, Staff_Orders_details
from van_management.models import Offload, Van, Van_Routes, VanCouponStock, VanProductItems, VanProductStock, VanSaleDamage

register = template.Library()

@register.simple_tag
def get_empty_bottles(salesman):
    try:
        return CustomerSupply.objects.filter(salesman=salesman,created_date__date=datetime.today().date()).aggregate(total=Coalesce(Sum('collected_empty_bottle'), Value(0)))['total']
    except CustomerSupply.DoesNotExist:
        return 0
    
@register.simple_tag
def get_van_product_wise_stock(date,van,product):
    if VanProductStock.objects.filter(created_date=date,van=van,product__pk=product).exists():
        if date:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            date = datetime.today().date()
            
        # print(date)
            
        van = Van.objects.get(pk=van)
        van_stock = VanProductStock.objects.get(created_date=date,van=van,product__pk=product)
            
        staff_order_details = Staff_Orders_details.objects.filter(staff_order_id__order_date=date,product_id__pk=product,staff_order_id__created_by=van.salesman.pk)
        # issue=Staff_IssueOrders.objects.filter(staff_Orders_details_id=staff_order_details)
        issued_count = staff_order_details.aggregate(total_count=Sum('issued_qty'))['total_count'] or 0
        
        total_stock = van_stock.stock + van_stock.opening_count
        sold_count = van_stock.sold_count
        
        extra_bottles = 0
        missed_bottles = 0
        
        customer_supply_item_details = CustomerSupplyItems.objects.filter(customer_supply__created_date__date=date,customer_supply__salesman__pk=van.salesman.pk,product__pk=product)
        
        cash_sale_qty = customer_supply_item_details.filter(customer_supply__amount_recieved__gt=0).aggregate(total_count=Sum('quantity'))['total_count'] or 0
        credit_sale_qty = customer_supply_item_details.filter(customer_supply__amount_recieved__lte=0).exclude(customer_supply__customer__sales_type__in=['CASH COUPON','FOC']).aggregate(total_count=Sum('quantity'))['total_count'] or 0
        coupon_sale_qty = customer_supply_item_details.filter(customer_supply__customer__sales_type='CASH COUPON').aggregate(total_count=Sum('quantity'))['total_count'] or 0
        foc_sale_qty = customer_supply_item_details.filter(customer_supply__allocate_bottle_to_free__gt=0).aggregate(total_count=Sum('customer_supply__allocate_bottle_to_free'))['total_count'] or 0
        foc_sale_qty += customer_supply_item_details.filter(customer_supply__customer__sales_type='FOC').aggregate(total_count=Sum('quantity'))['total_count'] or 0
        
        created_by_value = str(van.salesman.pk) if van.salesman else None
        custody_cash_sales_qs = CustodyCustomItems.objects.filter(
            custody_custom__created_date__date=date,
            product__pk=product,
            custody_custom__sales_type='CASH'
        )
        custody_credit_sales_qs = CustodyCustomItems.objects.filter(
            custody_custom__created_date__date=date,
            product__pk=product,
            custody_custom__sales_type='CREDIT'
        )
        custody_coupon_sales_qs = CustodyCustomItems.objects.filter(
            custody_custom__created_date__date=date,
            product__pk=product,
            custody_custom__sales_type='COUPON'
        )

        # If created_by stores salesman.pk or username as text
        if created_by_value:
            custody_cash_sales_qs = custody_cash_sales_qs.filter(custody_custom__created_by=created_by_value)
            custody_credit_sales_qs = custody_credit_sales_qs.filter(custody_custom__created_by=created_by_value)
            custody_coupon_sales_qs = custody_coupon_sales_qs.filter(custody_custom__created_by=created_by_value)

        custody_cash_sales = custody_cash_sales_qs.aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
        custody_credit_sales = custody_credit_sales_qs.aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
        custody_coupon_sales = custody_coupon_sales_qs.aggregate(total_qty=Sum('quantity'))['total_qty'] or 0

        # Add to main totals
        cash_sale_qty += custody_cash_sales
        credit_sale_qty += custody_credit_sales
        coupon_sale_qty += custody_coupon_sales
        
        for cs_item in customer_supply_item_details:
            
            item_quantity = cs_item.quantity
            item_foc_qty = cs_item.customer_supply.allocate_bottle_to_free
            item_collected_qty = cs_item.customer_supply.collected_empty_bottle
            
            excess_bottle = item_collected_qty - (item_quantity + item_foc_qty)
            if excess_bottle > 0:
                extra_bottles += excess_bottle
            if excess_bottle < 0 :
                missed_bottles += abs(excess_bottle)
        
        customer_custody_qty = 0
        customer_return_qty = 0
        
        van_route = Van_Routes.objects.filter(van=van).first()
        
        customer_custody_qty = CustodyCustomItems.objects.filter(
            custody_custom__created_date__date=date,
            custody_custom__created_by=van.salesman,
            product__pk=product
        ).aggregate(total_count=Sum('quantity'))['total_count'] or 0
        
        customer_return_qty = CustomerReturnItems.objects.filter(
            customer_return__created_date__date=date,
            customer_return__customer__routes=van_route.routes if van_route else None,
            product__pk=product
        ).aggregate(total_count=Sum('quantity'))['total_count'] or 0
                
        customer_custody_qty = CustodyCustomItems.objects.filter(custody_custom__created_date__date=date,custody_custom__customer__routes__route_name=van.get_vans_routes(),product__pk=product, custody_custom__sales_type__isnull=False).aggregate(total_count=Sum('quantity'))['total_count'] or 0
        customer_return_qty = CustomerReturnItems.objects.filter(customer_return__created_date__date=date,customer_return__customer__routes__route_name=van.get_vans_routes(),product__pk=product).aggregate(total_count=Sum('quantity'))['total_count'] or 0
        
        damage_instances = VanSaleDamage.objects.filter(created_date__date=date,created_by=van.salesman.pk,product__pk=product)
        leak_bottle_count = damage_instances.filter(reason__reason__iexact="leak").aggregate(total_count=Sum('quantity'))['total_count'] or 0
        damage_bottle_count = damage_instances.filter(reason__reason__iexact="damage").aggregate(total_count=Sum('quantity'))['total_count'] or 0
        service_bottle_count = damage_instances.filter(reason__reason__iexact="service").aggregate(total_count=Sum('quantity'))['total_count'] or 0
        leak_service_bottle_count = leak_bottle_count + service_bottle_count
        
        empty_stock = abs(customer_return_qty + van_stock.empty_can_count )
        fresh_stock = van_stock.stock
        
        offload_instances = Offload.objects.filter(van=van,product__pk=product,created_date__date=date)
        offload_count = offload_instances.aggregate(total_count=Sum('quantity'))['total_count'] or 0
        
        if offload_instances :
            empty_stock += offload_instances.filter(stock_type__in=["emptycan","empty_can"]).aggregate(total_count=Sum('quantity'))['total_count'] or 0
            fresh_stock += offload_instances.filter(stock_type__in=["stock"]).aggregate(total_count=Sum('quantity'))['total_count'] or 0
        
        # Get previous day's offload
        prev_date = date - timedelta(days=1)
        prev_offload_instances = Offload.objects.filter(van=van,product__pk=product,created_date__date=prev_date)
        
        
        if not prev_offload_instances:
            pre_van_stock = VanProductStock.objects.get(created_date=prev_date,van=van,product__pk=product)
            empty_stock -= pre_van_stock.empty_can_count
            fresh_stock -= pre_van_stock.stock
        
        return {
            "opening_stock": van_stock.opening_count,
            "requested_count": Staff_Orders_details.objects.filter(product_id__pk=product,staff_order_id__created_date__date=date,created_by=van.salesman.pk).aggregate(total_count=Sum('count'))['total_count'] or 0,
            "issued_count": issued_count,
            "net_load": van_stock.opening_count + issued_count,
            
            "cash_sale_qty": cash_sale_qty,
            "credit_sale_qty": credit_sale_qty,
            "coupon_sale_qty": coupon_sale_qty,
            "foc_sale_qty": foc_sale_qty,
            "net_sales_qty": cash_sale_qty + credit_sale_qty + coupon_sale_qty + foc_sale_qty ,
            
            "extra_bottles": extra_bottles,
            "return_qty": customer_return_qty,
            "missed_bottles": missed_bottles,
            "custody_issued_qty": customer_custody_qty,
            
            "leak_service_bottle_count": leak_service_bottle_count,
            "damage_bottle_count": damage_bottle_count,
            "empty_stock": empty_stock,
            "fresh_stock": fresh_stock,
            "offload_count": offload_count,
        }
    
@register.simple_tag
def get_five_gallon_ratewise_count(rate,date,salesman):
    instances = CustomerSupplyItems.objects.filter(customer_supply__created_date__date=date,customer_supply__salesman_id=salesman,product__product_name="5 Gallon",customer_supply__customer__rate=rate)
    return {
        "debit_amount_count": instances.filter(customer_supply__amount_recieved__gt=0).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0,
        "credit_amount_count": instances.filter(customer_supply__amount_recieved=0).exclude(customer_supply__customer__sales_type__in=["FOC","CASH COUPON"]).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0,
        "coupon_amount_count": instances.filter(customer_supply__customer__sales_type="CASH COUPON").aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    }
    
@register.simple_tag
def get_coupon_vanstock_count(van_pk,date,coupon_type):
    return VanCouponStock.objects.filter(created_date=date,van__pk=van_pk,coupon__coupon_type__coupon_type_name=coupon_type).aggregate(total_stock=Sum('stock'))['total_stock'] or 0
    

@register.simple_tag
def get_van_coupon_wise_stock(date, van, coupon):
    if van != "" and coupon != "" and date != "":
        if VanCouponStock.objects.filter(created_date=date, van=van, coupon__pk=coupon).exists():
            if date:
                date = datetime.strptime(date, '%Y-%m-%d').date()
            else:
                date = datetime.today().date()

            van = Van.objects.get(pk=van)
            van_stock = VanCouponStock.objects.get(created_date=date, van=van, coupon__pk=coupon)

            staff_order_details = Staff_Orders_details.objects.filter(
                staff_order_id__created_date__date=date,
                product_id__pk=coupon,
                staff_order_id__created_by=van.salesman.pk
            )
            issued_count = staff_order_details.aggregate(total_count=Sum('issued_qty'))['total_count'] or 0

            total_stock = van_stock.stock + van_stock.opening_count
            sold_count = van_stock.sold_count
            offload_count = Offload.objects.filter(
                van=van,
                product__pk=coupon,
                created_date__date=date
            ).aggregate(total_count=Sum('quantity'))['total_count'] or 0

            return {
                "opening_stock": van_stock.opening_count,
                "requested_count": Staff_Orders_details.objects.filter(
                    product_id__pk=coupon,
                    staff_order_id__created_date__date=date,
                    created_by=van.salesman.pk
                ).aggregate(total_count=Sum('count'))['total_count'] or 0,
                "issued_count": issued_count,
                "return_count": van_stock.return_count,
                "sold_count": sold_count,
                "closing_count": van_stock.closing_count,
                "offload_count": offload_count,
                "change_count": van_stock.change_count,
                "damage_count": van_stock.damage_count,
                "total_stock": total_stock
            }
    return {}


@register.simple_tag
def get_van_coupon_name_wise_stock(date, van, coupon_name):
    cash_coupon_reachage_count = 0
    credit_coupon_reachage_count = 0
    net_coupon_reachage_count = 0
    # print(coupon_name)
    if (coupon_instances:=VanCouponStock.objects.filter(created_date=date, van=van, coupon__coupon_type__coupon_type_name=coupon_name)).exists():
        
        staff_order_details = Staff_Orders_details.objects.filter(
            staff_order_id__created_date__date=date,
            product_id__product_name=coupon_name,
            staff_order_id__created_by=Van.objects.get(pk=van).salesman.pk
        )
        issued_count = staff_order_details.aggregate(total_count=Sum('issued_qty'))['total_count'] or 0

        offload_count = Offload.objects.filter(
            van=van,
            product__product_name=coupon_name,
            created_date__date=date
        ).aggregate(total_count=Sum('quantity'))['total_count'] or 0
        
        coupon_reachage_instances = CustomerCouponItems.objects.filter(customer_coupon__created_date__date=date, customer_coupon__salesman__pk=Van.objects.get(pk=van).salesman.pk, coupon__coupon_type__coupon_type_name=coupon_name)
        
        cash_coupon_reachage_count = coupon_reachage_instances.filter(customer_coupon__amount_recieved__gt=0).count()
        credit_coupon_reachage_count = coupon_reachage_instances.filter(customer_coupon__amount_recieved__lte=0).count()
        net_coupon_reachage_count = cash_coupon_reachage_count + credit_coupon_reachage_count
        
        opening_total = coupon_instances.aggregate(total_count=Sum('opening_count'))['total_count'] or 0
        
        return {
            "opening_stock": coupon_instances.aggregate(total_count=Sum('opening_count'))['total_count'] or 0,
            "requested_count": Staff_Orders_details.objects.filter(
                product_id__product_name=coupon_name,
                staff_order_id__created_date__date=date,
                created_by=Van.objects.get(pk=van).salesman.pk
            ).aggregate(total_count=Sum('count'))['total_count'] or 0,
            "issued_count": issued_count,
            "net_load": opening_total + issued_count,
            
            "cash_coupon_reachage_count": cash_coupon_reachage_count,
            "credit_coupon_reachage_count": credit_coupon_reachage_count,
            "net_coupon_reachage_count": net_coupon_reachage_count,
            
            "return_count": coupon_instances.aggregate(total_count=Sum('return_count'))['total_count'] or 0,
            "sold_count": coupon_instances.aggregate(total_count=Sum('sold_count'))['total_count'] or 0,
            "closing_count": coupon_instances.aggregate(total_count=Sum('closing_count'))['total_count'] or 0,
            "offload_count": offload_count,
            "change_count": coupon_instances.aggregate(total_count=Sum('change_count'))['total_count'] or 0,
            "damage_count": coupon_instances.aggregate(total_count=Sum('damage_count'))['total_count'] or 0,
            "total_stock": coupon_instances.aggregate(total_count=Sum('stock'))['total_count'] or 0,
            "stock_count": coupon_instances.aggregate(total_count=Sum('stock'))['total_count'] or 0,
        }
        
        
# @register.simple_tag 
# def get_van_sales_office_report_summary(date, van, product):
#     # convert string date if needed
#     if isinstance(date, str):
#         date = datetime.strptime(date, '%Y-%m-%d').date()

#     van = Van.objects.get(pk=van)

#     # Get all load issues for this day
#     loads = Staff_Orders_details.objects.filter(
#         staff_order_id__order_date=date,
#         product_id__pk=product,
#         staff_order_id__created_by=van.salesman.pk,
#     ).order_by("created_date")  # make sure chronological

#     # Split into first load vs second load
#     first_load = 0
#     second_load = 0
#     if loads.exists():
#         # Take the first "created_date group" as first load
#         first_created = loads.first().created_date

#         first_load = loads.filter(
#             created_date=first_created
#         ).aggregate(total=Sum("issued_qty"))["total"] or 0

#         # Remaining same-day loads = second load
#         second_load = loads.exclude(
#             created_date=first_created
#         ).aggregate(total=Sum("issued_qty"))["total"] or 0

#     # Net load = total issued
#     issued_count = first_load + second_load

#     # Van stock
#     van_stock = VanProductStock.objects.filter(
#         created_date=date, van=van, product__pk=product
#     ).first()

#     # Sales details
#     customer_supply_items = CustomerSupplyItems.objects.filter(
#         customer_supply__created_date__date=date,
#         customer_supply__salesman__pk=van.salesman.pk,
#         product__pk=product
#     )

#     sale_qty = customer_supply_items.aggregate(total=Sum('quantity'))['total'] or 0

#     # Empty bottles returned
#     empty_stock = van_stock.empty_can_count if van_stock else 0

#     # Total bottles = sales + returns
#     btls_total = sale_qty + empty_stock

#     # Short bottles (expected – actual)
#     expected_return = sale_qty  # assumption: 1 return per sale
#     btls_short = max(expected_return - empty_stock, 0)

#     # Cancelled bottles
#     cancelled_btls = 0

#     # Extra returned
#     extra_rtn = max(empty_stock - expected_return, 0)

#     # New customer bottles (custody items issued)
#     new_cust = CustodyCustomItems.objects.filter(
#         custody_custom__created_date__date=date,
#         custody_custom__created_by=van.salesman.pk,
#         product__pk=product
#     ).aggregate(total=Sum('quantity'))['total'] or 0

#     # Extra given bottles = issued more than requested
#     extra_given = max(issued_count - (sale_qty + new_cust), 0)

#     # Damage / leak
#     damage_instances = VanSaleDamage.objects.filter(
#         created_date__date=date, created_by=van.salesman.pk, product__pk=product
#     )
#     leak = damage_instances.filter(reason__reason__iexact="leak").aggregate(total=Sum('quantity'))['total'] or 0

#     # Total bottles in = empty returns + extra returns + custody returns
#     total_btls_in = empty_stock + extra_rtn

#     # Next day load (carry forward)
#     next_day_load = van_stock.stock if van_stock else 0

#     return {
#         "issued_count": issued_count,
#         "second_load": second_load,
#         "net_load": issued_count + second_load,
#         "fresh_stock": van_stock.stock if van_stock else 0,
#         "net_sales_qty": sale_qty,
#         "empty_stock": empty_stock,
#         "btls_total": btls_total,
#         "btls_short": btls_short,
#         "cancelled_btls": cancelled_btls,
#         "extra_rtn": extra_rtn,
#         "new_cust": new_cust,
#         "extra_given": extra_given,
#         "leak": leak,
#         "total_btls_in": total_btls_in,
#         "next_day_load": next_day_load,
#         "cooler": CustodyCustomItems.objects.filter(
#             custody_custom__created_date__date=date,
#             custody_custom__created_by=van.salesman.pk,
#             product__product_name="Hot and Cool"
#         ).aggregate(total=Sum('quantity'))['total'] or 0,
#         "mtungi": CustodyCustomItems.objects.filter(
#             custody_custom__created_date__date=date,
#             custody_custom__created_by=van.salesman.pk,
#             product__product_name="Mutungi"
#         ).aggregate(total=Sum('quantity'))['total'] or 0,
#         "remarks": "",
#     }
        
@register.simple_tag
def get_van_sales_office_report_summary(date, van, product):
    if not van:
        return {}  # skip if no van id

    # Convert string date if needed
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    next_date = date + timedelta(days=1)

    try:
        van = Van.objects.get(pk=van)
    except (Van.DoesNotExist, ValueError, TypeError):
        return {}

    # --- Load Calculations ---
    all_loads = Staff_Orders_details.objects.filter(
        created_date__date=date,
        product_id__pk=product,
        staff_order_id__created_by=van.salesman.pk
    ).distinct()

    first_load_instance = all_loads.first()
    first_load = int(first_load_instance.issued_qty) if first_load_instance and first_load_instance.issued_qty else 0

    second_load_instance = all_loads.exclude(pk=first_load_instance.pk if first_load_instance else None).first()
    second_load = int(second_load_instance.issued_qty) if second_load_instance and second_load_instance.issued_qty else 0

    net_load = first_load + second_load

    # --- Van Stock ---
    van_stock = VanProductStock.objects.filter(
        created_date=date,
        van=van,
        product__pk=product
    ).distinct()

    # --- Customer Supply & Sales ---
    customer_supply_item_details = CustomerSupplyItems.objects.filter(
        customer_supply__created_date__date=date,
        customer_supply__salesman__pk=van.salesman.pk,
        product__pk=product
    ).distinct()

    cash_sale_qty = customer_supply_item_details.filter(customer_supply__amount_recieved__gt=0).aggregate(total=Sum('quantity'))['total'] or 0

    credit_sale_qty = customer_supply_item_details.filter(customer_supply__amount_recieved__lte=0).exclude(customer_supply__customer__sales_type__in=['CASH COUPON', 'FOC']).aggregate(total=Sum('quantity'))['total'] or 0

    coupon_sale_qty = customer_supply_item_details.filter(customer_supply__customer__sales_type='CASH COUPON').aggregate(total=Sum('quantity'))['total'] or 0

    foc_sale_qty = customer_supply_item_details.filter(customer_supply__allocate_bottle_to_free__gt=0).aggregate(total=Sum('customer_supply__allocate_bottle_to_free'))['total'] or 0

    foc_sale_qty += customer_supply_item_details.filter(customer_supply__customer__sales_type='FOC').aggregate(total=Sum('quantity'))['total'] or 0
    
    # *************************************** #
    # Custody Issue 
    customer_custody_instances = CustodyCustom.objects.filter(created_date__date=date, customer__routes__route_name=van.get_van_route, customer__is_deleted=False,  sales_type__isnull=False)
    fgallon_custody_instances = customer_custody_instances.filter(custodycustomitems__product__product_name="5 Gallon")
    
    cash_sale_qty += fgallon_custody_instances.filter(sales_type="CASH").aggregate(total_quantity=Sum('custodycustomitems__quantity'))['total_quantity'] or 0
    
    credit_sale_qty += fgallon_custody_instances.filter(sales_type="CREDIT").aggregate(total_quantity=Sum('custodycustomitems__quantity'))['total_quantity'] or 0
    
    coupon_sale_qty += fgallon_custody_instances.filter(sales_type="COUPON").aggregate(total_quantity=Sum('custodycustomitems__quantity'))['total_quantity'] or 0
    # *************************************** #

    fresh_stock = (van_stock.aggregate(total=Sum('opening_count'))['total'] or 0) + first_load + second_load
    net_sale_qty = cash_sale_qty + credit_sale_qty + coupon_sale_qty + foc_sale_qty

    customer_supply = CustomerSupply.objects.filter(
        pk__in=customer_supply_item_details.values_list("customer_supply__pk", flat=True)
    ).distinct()

    empty_bottle = customer_supply.aggregate(total=Sum('collected_empty_bottle'))['total'] or 0

    wtr_rtrn = net_load - net_sale_qty
    btls_in_total = wtr_rtrn + empty_bottle
    btls_status = net_load - btls_in_total
    
    customer_return = CustomerReturnItems.objects.filter(customer_return__created_date__date=date,customer_return__customer__routes__route_name=van.get_vans_routes())
    customer_return_qty = customer_return.aggregate(total_count=Sum('quantity'))['total_count'] or 0
    
    extra_given = customer_return_qty
    
    btls_short = btls_extra = 0
    if btls_status > 0:
        btls_short = btls_status
    elif btls_status < 0:
        btls_extra = abs(btls_status)

    new_cust = CustodyCustomItems.objects.filter(
        custody_custom__created_date__date=date,
        custody_custom__created_by=van.salesman.pk,
        product__pk=product
    ).distinct().aggregate(total=Sum('quantity'))['total'] or 0

    damage_instances = VanSaleDamage.objects.filter(
        created_date__date=date,
        created_by=van.salesman.pk,
        product__pk=product
    ).distinct()

    leak = damage_instances.filter(
        reason__reason__iexact="leak"
    ).aggregate(total=Sum('quantity'))['total'] or 0

    total_btls_in = net_load + btls_extra - new_cust - leak - btls_short

    next_day_request_instance = Staff_Orders_details.objects.filter(
        staff_order_id__created_date__date=next_date,
        staff_order_id__created_by=van.salesman.pk
    ).distinct().first()
    next_day_request = next_day_request_instance.count if next_day_request_instance else 0

    cooler = CustodyCustomItems.objects.filter(
        custody_custom__created_date__date=date,
        custody_custom__created_by=van.salesman.pk,
        product__product_name="Hot and Cool"
    ).distinct().aggregate(total=Sum('quantity'))['total'] or 0

    mtungi = CustodyCustomItems.objects.filter(
        custody_custom__created_date__date=date,
        custody_custom__created_by=van.salesman.pk,
        product__product_name="Mutungi"
    ).distinct().aggregate(total=Sum('quantity'))['total'] or 0

    return {
        "issued_count": first_load,
        "second_load": second_load,
        "net_load": net_load,
        "wtr_rtrn": wtr_rtrn,
        "net_sales": net_sale_qty,
        "empty_btls_return": empty_bottle,
        "btls_in_total": btls_in_total,
        "btls_short": btls_short,
        "cancelled_btls": 0,
        "extra_rtn": btls_extra,
        "new_cust": new_cust,
        "leak": leak,
        "extra_given": extra_given,
        "total_btls_in": total_btls_in,
        "next_day_load": total_btls_in + (next_day_request or 0),
        "cooler": cooler,
        "mtungi": mtungi,
        "remarks": "",
    }