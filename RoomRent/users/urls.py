from django.urls import path
from . import views

# PASSWORD RESET
from django.contrib.auth import views as auth_views

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

     # PASSWORD RESET
    path('reset-password', auth_views.PasswordResetView.as_view(
    template_name="Authentication/Forgot Password/resetPassword.html"), 
    name="reset_password"),   
    
    path('reset-password-sent', auth_views.PasswordResetDoneView.as_view(
    template_name="Authentication/Forgot Password/resetPasswordSent.html"), 
    name="password_reset_done"), 
      
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
    template_name="Authentication/Forgot Password/resetPasswordConfirm.html"), 
    name="password_reset_confirm"), 
      
    path('reset-password-complete', auth_views.PasswordResetCompleteView.as_view(
    template_name="Authentication/Forgot Password/resetPasswordComplete.html"), 
    name="password_reset_complete"),  
]