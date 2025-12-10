import os
import django
import openpyxl
from datetime import date

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from client_management.models import OutstandingAmount
from django.db import connection

def get_zero_outstanding_last_month():
    sql = """
        SELECT 
            ao.id,
            ao.amount,
            ao.customer_outstanding_id,
            co.invoice_no
        FROM client_management_outstandingamount ao
        JOIN client_management_customeroutstanding co
            ON ao.customer_outstanding_id = co.id
        WHERE ao.amount = 0
          AND DATE(co.created_date) BETWEEN %s AND %s
        ORDER BY co.created_date DESC;
    """

    start_date = "2025-09-25"
    end_date = "2025-10-30"

    with connection.cursor() as cursor:
        cursor.execute(sql, [start_date, end_date])
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    return [dict(zip(columns, row)) for row in rows]


def export_zero_outstanding_excel():
    print("Generating Excel...")

    data = get_zero_outstanding_last_month()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Zero Outstanding"

    # Header row
    ws.append(["ID", "Invoice No", "Amount", "Customer Outstanding ID"])

    # Data rows
    for row in data:
        ws.append([
            row["id"],
            row["invoice_no"],
            float(row["amount"]),
            row["customer_outstanding_id"],
        ])

    file_name = "zero_outstanding.xlsx"
    wb.save(file_name)

    print(f"Excel created: {file_name}")


# Run export
export_zero_outstanding_excel()
