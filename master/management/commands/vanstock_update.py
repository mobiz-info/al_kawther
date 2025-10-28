from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Update van stock daily.'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        print(f"Updating van stock: Yesterday was {yesterday}")
        # Your logic to update van stock goes here
