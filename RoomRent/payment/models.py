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
    electricityUnit = models.IntegerField(default=0)
    electricityAmount = models.IntegerField(default=0)
    totalRoomRentAmount = models.IntegerField(default=0)
    electricityPreviousUnit = models.IntegerField(default=0, blank=False) 
    electricityCurrentUnit = models.IntegerField(default=0, blank=False) 
    status = models.CharField(max_length=50, default='pending') # it can be [ updated, paid, pending ]
    hasChargeLatePaymentFee = models.BooleanField(default=False) # if owner update to charge late payment Fee then tenant will be charge else they will not be charge if it is late
