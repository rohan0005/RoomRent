from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(RoomImage)
admin.site.register(Room)
admin.site.register(RoomDocument)
admin.site.register(BookRoom)
admin.site.register(RoomFeedbacks)
admin.site.register(ElectricityUnitDetail)
admin.site.register(BookingLog)
admin.site.register(CanceledBooking)