from django.core.management.base import BaseCommand
from agriapp.views import update_equipment_status

class Command(BaseCommand):
    help = 'Updates equipment status once a day'

    def handle(self, *args, **kwargs):
        update_equipment_status()
        self.stdout.write("Status updated successfully!")