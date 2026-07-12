from datetime import date
from .views import update_equipment_status

class EquipmentStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Fakt divasatil pahilya request sathi check karel
        update_equipment_status()
        response = self.get_response(request)
        return response