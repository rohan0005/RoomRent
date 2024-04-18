from django.urls import path
from . import views

urlpatterns = [

    path('initiate',views.initkhalti,name="initiate"),
    path('verify',views.verifyKhalti,name="verify"),
    path('billing',views.billing,name="billing"),
    path('paymentHistory',views.paymentHistory,name="paymentHistory"),
    path('admin/paymentHistory',views.paymentHistoryAdminView,name="paymentHistoryAdmin"),
    
]