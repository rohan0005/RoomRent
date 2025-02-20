from django.shortcuts import render
from .models import *
from room.models import Room, BookRoom
import sweetify
from django.contrib.auth.decorators import login_required, user_passes_test
from userManagement.checkUserGroup import *

# Create your views here.
def index(request):
    if request.user is not None and request.user.is_authenticated:
        roomInstance = Room.objects.filter(user=request.user)
        for room in roomInstance:
            bookings = BookRoom.objects.filter(room = room, joined=False).first()
            if bookings:
                sweetify.info(request, "You have a pending bookings. Please visit dashboard.", button='Ok', timer=0)
    return render(request, 'Landing page/index.html')

def checkValidity(request):
    if request.user is not None and not request.user.is_superuser and request.user.is_authenticated and not request.user.groups.filter(name='owner') and not request.user.groups.filter(name='tenant'):
        sweetify.warning(request, 'Please wait before admin approves your account.', button='Ok', timer=0)
    
    elif request.user.is_authenticated and (request.user.is_superuser or request.user.groups.filter(name='owner') or  request.user.groups.filter(name='tenant')):
        return render(request, '505_404.html')
        
    else:
        sweetify.error(request, 'You are not authorized to view this page.', button='Ok', timer=0)    
    return render(request, 'Landing page/index.html')

def contact(request):
    try:
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
                
    except:
        sweetify.error(request, 'Something went Wrong!',  button='Ok', timer=0)
        return redirect('index')

@user_passes_test(is_superuser)
def contactFromUser(request):
    try:
        if request.method == 'POST' and "markAsRead" in request.POST:
            id = request.POST.get('ContactID')
            contactUsUpdate = ContactUsDetail.objects.get(pk=id)
            contactUsUpdate.status = "checked"
            contactUsUpdate.save()
            sweetify.success(request, 'User message marked as read !!',   button='Ok', timer=0)
            
        contactUsData = ContactUsDetail.objects.all()
        context = { 
            'contactUsData' : contactUsData
        }
        return render(request, 'Admin/contactFromUser.html', context)
    except:
        sweetify.error(request, 'Something went wrong!',   button='Ok', timer=0)
        return redirect('index')
    
def error_404(request, exception):
    print(hh)
    return render(request, '505_404.html', status=404)
 
def error_500(request):
    return render (request, '505_404.html', status=500)