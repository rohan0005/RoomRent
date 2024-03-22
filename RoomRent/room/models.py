from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Model to store Room details
class Room(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    roomTitle = models.CharField(max_length=50,blank=False)
    roomDescription = models.TextField(blank=False)
    roomAddress = models.CharField(max_length=50,blank=False)
    detailedRoomAddress = models.TextField(blank=False)
    floor = models.CharField(max_length=50,blank=False)
    rules= models.TextField(default="No Rules are added to this room")
    numberOfBathroom = models.IntegerField(blank=False)
    flat = models.CharField(max_length=50,blank=False)
    parking = models.CharField(max_length=50,blank=False)
    amenities = models.TextField(blank=False)
    electricity = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    water = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    trash = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    rent = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    isAvailable = models.BooleanField(default=True)
    isBooked = models.BooleanField(default=False)
    listed_date = models.DateTimeField(default=timezone.now, blank=True)
    approved = models.BooleanField(blank=False, default=False) 
    
    
    def __str__(self):
        return f"{self.roomTitle} by {self.user.username}"

class RoomFeedbacks(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback = models.TextField(blank=True)
    


# Model to store Room Images
class RoomImage(models.Model):
    room = models.ForeignKey(Room, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='Room Images')

# Model to store Room or property related Documents
class RoomDocument(models.Model):
    room = models.ForeignKey(Room, related_name='documents', on_delete=models.CASCADE)
    document = models.FileField(upload_to='Room Document')
    
    
class BookRoom(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bookingDate = models.DateTimeField(default=timezone.now)
    moveInDate = models.DateTimeField(default=timezone.now) 
    joined = models.BooleanField(default=False)
    moveOutDate = models.DateTimeField(null=True, blank=True)
    rentBilledDate = models.DateTimeField(null=True, blank=True, default= None)
    def __str__(self):
        return f"{self.user}'s booking"
    
    
class ElectricityUnitDetail(models.Model):
    bookedRoom = models.OneToOneField(BookRoom, on_delete= models.CASCADE)
    electricityPreviousUnit = models.IntegerField(default=0, blank=False); 
    electricityCurrentUnit = models.IntegerField(default=0, blank=False); 
    status = models.CharField(max_length=50, blank=False, default='Pending update')  # Pending update or Updated
    
class BookingLog(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bookingDate = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, default='Cancelled')
    

class CanceledBooking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bookingDate = models.DateTimeField(default=timezone.now)
    canceledDate = models.DateTimeField(default=timezone.now)
    