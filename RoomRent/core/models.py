from django.db import models
from django.utils import timezone

# Create your models here.
class ContactUsDetail(models.Model):
    fullName = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    message = models.TextField()
    contactedOn = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50,default='pending')