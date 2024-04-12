from django.shortcuts import render
from .models import *
import sweetify
from django.contrib.auth.decorators import login_required, user_passes_test
from userManagement.checkUserGroup import *

# Create your views here.
def index(request):
    return render(request, 'Landing page/index.html')

def checkValidity(request):
    sweetify.error(request, 'You are not authorized to view this page.', button='Ok', timer=0)
    return render(request, 'Landing page/index.html')

def contact(request):
    if request.method == 'POST':
        if request.user.is_superuser:
            sweetify.error(request, 'You cannot submit this form.',  button='Ok', timer=0)
        else:
            fullname = request.POST.get('fullName')
            email = request.POST.get('email')
            message = request.POST.get('message')
            contactUs = ContactUsDetail.objects.create(fullName=fullname, email=email, message=message)
            contactUs.save()
            sweetify.success(request, 'Thank you for you feedback. We will reach out to you soon',  button='Ok', timer=0)
    return render(request, 'Landing page/contactUs.html')

@user_passes_test(is_superuser)
def contactFromUser(request):
    try:
        if request.method == 'POST' and "markAsRead" in request.POST:
            id = request.POST.get('ContactID')
            contactUsUpdate = ContactUsDetail.objects.get(pk=id)
            contactUsUpdate.status = "checked"
            contactUsUpdate.save()
            sweetify.success(request, 'User message marked as read !!',   button='Ok', timer=0)
    except:
        sweetify.success(request, 'Something went wrong.',   button='Ok', timer=0)
        
    contactUsData = ContactUsDetail.objects.all()
    context = { 
        'contactUsData' : contactUsData
    }
    return render(request, 'Admin/contactFromUser.html', context)

def error_404(request, exception):
    print(hh)
    return render(request, '505_404.html', status=404)
 
def error_500(request):
    return render (request, '505_404.html', status=500)