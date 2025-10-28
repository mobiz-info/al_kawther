import datetime
from django.core.management.base import BaseCommand
from accounts.models import Customers, Send_Notification
from apiservices.notification import notification
from apiservices.views import find_customers
from master.models import RouteMaster

class Command(BaseCommand):
    help = 'Customer Previous Day Notification'

    def handle(self, *args, **kwargs):
        routes = RouteMaster.objects.all()
        date_today = datetime.date.today()
        date_today_str = date_today.strftime('%Y-%m-%d')  # Convert date to string in the correct format

        for route in routes:
            # try:
            # Assuming 'find_customers' expects a string date
            customers_for_tomorrow = find_customers(None, date_today_str, route.route_id)
            
            if customers_for_tomorrow is None:
                    self.stdout.write(self.style.WARNING(f'No customers found for route {route.route_id} on {date_today_str}'))
                    continue
            
            for customer in customers_for_tomorrow:
                customer_id = str(customer['customer_id'])
                try:
                    user_id = Customers.objects.get(pk=customer_id).user_id.pk
                    # Sending notification
                    if Send_Notification.objects.filter(user__pk=user_id).exists():
                        notification(user_id, "Reminder", "Your Van will be arriving tomorrow. Please keep your cap outside.", "Nationalwatercustomer")
                        
                except:
                    pass
            # except Exception as e:
            #     self.stdout.write(self.style.ERROR(f'Error processing route {route.route_id}: {e}'))
                # continue  # Continue with the next route in case of an error

        self.stdout.write(self.style.SUCCESS('Notifications sent successfully for all customers.'))
