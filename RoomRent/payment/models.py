from django.db import models
from room.models import BookRoom, Room
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
    
class RoomBilling(models.Model):
    bookedRoom = models.OneToOneField(BookRoom, on_delete=models.CASCADE)
    electricityUnit = models.IntegerField(default=0)
    electricityAmount = models.IntegerField(default=0)
    totalRoomRentAmount = models.IntegerField(default=0)
    electricityPreviousUnit = models.IntegerField(default=0, blank=False) 
    electricityCurrentUnit = models.IntegerField(default=0, blank=False) 
    status = models.CharField(max_length=50, default='pending') # it can be [ updated, paid, pending ]
    hasChargeLatePaymentFee = models.BooleanField(default=False) # if owner update to charge late payment Fee then tenant will be charge else they will not be charge if it is late
    deposit = models.IntegerField(default=0) # To store deposit amount that tenant will pay
    
class PaymentHistory(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    tenantUser = models.ForeignKey(User, on_delete=models.CASCADE)
    paidDate = models.DateTimeField(default=timezone.now)
    billedDate = models.DateTimeField(blank=False)
    lateDays = models.IntegerField(blank=False)
    lateFee = models.IntegerField(blank=False)
    depositedAmount = models.IntegerField(blank=False)
    totalPaidAmount = models.IntegerField(blank=False)
    transactionID = models.CharField(blank=False, max_length=100)
    hasReleasedFund = models.BooleanField(default=False)
    systemCommissionAmount = models.IntegerField(default=0)