from django.db import models
from django.contrib.auth.models import User

# This model stores user additional info like: address and contact number
class UserAdditionalDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=15,blank=False)
        
    def __str__(self):
        return f"{self.user.username}'s Details"
        
# This model stores user profile pictures 
class UserProfilePicture(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # By default uploading default user image from User default profile folder then uploading it inside User profile folder
    image = models.ImageField(default='Profile pictures/User default profile/DefaultUser.png',blank=False,upload_to='User profile')

    def __str__(self):
        return f'{self.user.username} Profile Picture'

# This model stores user additional info like: address and contact number
class UserCitizenship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(blank=False,upload_to='Owner Citizenship')
    
    def __str__(self):
        return f'{self.user.username} Citizenship'
