from django.urls import path
from . import views

urlpatterns = [

    path('initiate',views.initkhalti,name="initiate"),
    path('verify',views.verifyKhalti,name="verify"),
    path('error',views.error,name="error"),
    path('billing',views.billing,name="billing"),
    
]