from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from .models import *
from .forms import *
from django.db import transaction
from django.contrib.auth.models import Group
# SEND MAIL
from django.core.mail import send_mail


# SIGNUP UP NEW USERS
def SignupUser(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST, request.FILES) # Get the form data and if user uploads files get files too 
        if form.is_valid():
        # Get the username
            username = form.cleaned_data.get('username')
            # An atomic transaction guarantees that all operations within the block are treated as a single unit. 
            # If any operation fails, the entire transaction is rolled back, 
            # undoing all changes made within the block.
            with transaction.atomic():
                user = form.save()
                # saving user contact number and address
                details = UserAdditionalDetail(user=user, contact_number=request.POST.get('contact'))
                details.save()
                
                # Saving user default profile
                # We can just call the model it will save the default picture
                default_picture = UserProfilePicture(user=user)
                default_picture.save()
                

                # if user choose to become owner then they should upload document
                if request.FILES:
                    images=request.FILES.getlist('document_image')
                    
                    for citizenship_image in images:
                        citizenship = UserCitizenship(user=user, image=citizenship_image)
                        citizenship.save()
                    messages.success(request,"Account Created for " + username + " Please wait before we verify.")                  
                
                # If user choose to become tenant then adding them to tenant group
                else:
                    group, created = Group.objects.get_or_create(name='tenant')
                    user.groups.add(group)
                    messages.success(request,"Account Created for " + username)
                    
            return redirect('signin')        
              
    
    return render(request,'Authentication/signin and signup/signup.html')

# SIGNIN USERS
def SigninUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        # Checking if user exist or not
        if user is not None and user.is_superuser or(user is not None and user.groups.filter(name__in=['owner', 'tenant']).exists()):
            login(request, user)
             
            return redirect('/')
        
        elif user is not None and not user.groups.exists():
            
            messages.info(request, 'User is not approved.')

        else:
            messages.info(request, 'Username or Password is incorrect')

    return render(request, 'Authentication/signin and signup/signin.html')

# SIGNOUT USER
def signoutUser(request):
    logout(request)
    return redirect('signin')

# return superuser
def is_superuser(user):
    return user.is_superuser


# Admin Pages
@login_required(login_url='signin')
@user_passes_test(is_superuser)
def adminDashboard(request):
    
    allVerifiedUsers = User.objects.filter(groups__name__in=['owner', 'tenant'])
    totalVerifiedUsers = User.objects.filter(groups__name__in=['owner', 'tenant']).count()       

    totalUsersWhoRequestForOwner = User.objects.filter(groups__isnull=True).exclude(is_superuser=True).count()


    context = {
        'allVerifiedUsers': allVerifiedUsers,
        'totalVerifiedUsers' : totalVerifiedUsers,
        'totalUsersWhoRequestForOwner' : totalUsersWhoRequestForOwner,
        
        
    }
    return render(request, 'Admin/adminDashboard.html', context)

@login_required(login_url='signin')
@user_passes_test(is_superuser)
def pendingRequests(request):
    
    usersWhoRequestForOwner = User.objects.filter(groups__isnull=True).exclude(is_superuser=True)

    
    context = {
        
        'usersWhoRequestForOwner': usersWhoRequestForOwner,
        
    }
    
    return render(request, 'Admin/pendingRequests.html', context)



@login_required(login_url='signin')
@user_passes_test(is_superuser)
def detailPendingRequestsUser(request, userID):
    # Get the username
    user = get_object_or_404(User, id=userID)

    citizenship = UserCitizenship.objects.filter(user=user)
    
    
    if request.method == 'POST':
        if "approve" in request.POST:
            if "user" in request.POST:
                username = request.POST.get("user")
                user = User.objects.get(username=username)
                
                user_email = user.email
                
                # GROUP as Owner after approval
                group, created = Group.objects.get_or_create(name='owner')
                user.groups.add(group)
                
                # Sending mail after user is approved
                send_mail(
                "Owner request approved",
                "Your account has been approved as an Owner on RoomRent website. You can now login and List your Rooms",
                "room.rent.webapp@gmail.com",
                [user_email],
                fail_silently=False,
                )
                
                
                return redirect('adminDashboard')
            
        # IF ADMIN CLICKS REJECT
        else:
            if "user" in request.POST:
                username = request.POST.get("user")
                user = User.objects.get(username=username)
                user_email = user.email 
                # Sending mail after user is approved
                send_mail(
                    "Account Rejected",
                    "Your account has been rejected as an Owner on RoomRent website due to certain reasons or invalid citizenship.",
                    "room.rent.webapp@gmail.com",
                    [user_email],
                    fail_silently=False,)
                user.delete()
                return redirect('adminDashboard')
    
    
    context = {
        'requestedUser': user,
        'citizenship' : citizenship,
    }
    
    return render(request, 'Admin/pendingRequests-user.html', context)
