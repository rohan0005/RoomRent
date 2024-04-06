from django.urls import path
from . import views

urlpatterns = [
    path('listing', views.listing, name='listing'), 
    path('user/admin/pendingRooms', views.pendingRooms, name='pendingRooms'), 
    path('myRoom', views.myRoom, name='myRoom'),
    path('room', views.room, name='room'),
    path('room/details/<int:room_id>', views.roomMoreDetails, name='roomMoreDetails'),
    
    path('dashboard/viewBooking', views.viewBooking, name='viewBooking'),  
    
    
]