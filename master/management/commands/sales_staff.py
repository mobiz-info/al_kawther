import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Customers,CustomUser
from master.models import RouteMaster

User = get_user_model()

class Command(BaseCommand):
    help = "Assign all DM route customers to sales staff 'Abijith123'"

    def handle(self, *args, **kwargs):
        try:
            # get sales staff user
            sales_user = CustomUser.objects.get(username="Moquait123")

            # get DM route (assuming route name = "DM")
            dm_route = RouteMaster.objects.get(route_name="SL")

            # update all customers in that route
            updated_count = Customers.objects.filter(routes=dm_route).update(sales_staff=sales_user)

            self.stdout.write(self.style.SUCCESS(
                f"✅ Successfully updated {updated_count} customers in DM route to sales_staff Abijith123"
            ))

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ User 'Abijith123' not found."))
        except RouteMaster.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Route 'DM' not found."))