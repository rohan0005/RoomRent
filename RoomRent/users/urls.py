from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.SignupUser, name='signup'),
    path('signin', views.SigninUser, name='signin'),
    path('signout', views.signoutUser, name='signout'),
     
     # Admin routes
    path('adminDashboard', views.adminDashboard, name='adminDashboard'),
    path('pendingRequests', views.pendingRequests, name='pendingRequests'),
    
     # Owner and Tenant routes
    # path('owner/dashboard', views.ownerDashboard, name='ownerDashboard'),
    path('dashboard', views.dashboard, name='dashboard'),   
    path('dashboard/editProfile', views.editProfile, name='editProfile'), 
    path('dashboard/changePassword', views.changePassword, name='changePassword'),   
    path('activate/<uidb64>/<token>', views.activate, name='activate'),

    
]