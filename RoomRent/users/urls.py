from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.SignupUser, name='signup'),
    path('signin', views.SigninUser, name='signin'),
    path('signout', views.signoutUser, name='signout'),
     
     # Admin routes
    path('adminDashboard', views.adminDashboard, name='adminDashboard'),
    path('pendingRequests', views.pendingRequests, name='pendingRequests'),
    
    
    
    
    
]