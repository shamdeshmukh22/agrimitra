from django.contrib import admin
from .models import User_Detail, Categories, Equipment, Orders, RentalAdjustment

admin.site.register(User_Detail)
admin.site.register(Categories)
admin.site.register(Equipment)
admin.site.register(Orders)
admin.site.register(RentalAdjustment)