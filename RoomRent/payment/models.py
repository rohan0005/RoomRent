from django.db import models
from room.models import BookRoom
from django.utils import timezone

# Create your models here.
class MyBalance(models.Model):
    bookedRoom = models.OneToOneField(BookRoom, related_name = 'bookedRoom', on_delete=models.CASCADE)
    amount = models.DecimalField(default=0,max_digits=10, decimal_places=2, blank=False)
    amountUpdatedOn = models.DateTimeField(default=timezone.now)
    
    
class RoomBilling(models.Model):
    bookedRoom = models.OneToOneField(BookRoom, on_delete=models.CASCADE)
    electricityUnit = models.IntegerField(blank=False); 
    electricityAmount = models.IntegerField(blank=False); 
    totalRoomRentAmount = models.IntegerField(blank=False); 