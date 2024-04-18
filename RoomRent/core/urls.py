from django.urls import path
from . import views

urlpatterns = [
    path('home', views.index, name='index'), 
    path('home/', views.checkValidity, name='Dashboard'),   
    path('contactus', views.contact, name='contact'),   
    path('admin/contacts', views.contactFromUser, name='contactFromUser'),   
]