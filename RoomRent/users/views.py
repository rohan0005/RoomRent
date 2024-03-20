from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash # for authentication
from django.contrib import messages
from .models import *
from .forms import *
from django.db import transaction
from django.contrib.auth.models import Group
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger #for pagination 
from django.core.mail import send_mail # For sending email notifications

import sweetify

# Main logis are written in the views.py

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
                    
                    # Store the citizenship image
                    for citizenship_image in images:
                        citizenship = UserCitizenship(user=user, image=citizenship_image)
                        citizenship.save()
                    sweetify.success(request,"Account Created for " + username)                  
                
                # If user choose to become tenant then adding them to tenant group
                else:
                    group, created = Group.objects.get_or_create(name='tenant')
                    user.groups.add(group)
                    sweetify.success(request,"Account Created for " + username)
            return redirect('signin') # After creating the user redirect to the signin page
        # If form is not valid
        elif not form.is_valid():
            errorMessage = next(iter(form.errors.values()))[0]     # Retrieving the first error message from the form errors
            sweetify.error(request, errorMessage)
            
    return render(request,'Authentication/signin and signup/signup.html')

# SIGNIN USERS
def SigninUser(request):
    if request.method == 'POST':
        # request and assign the user name and password to the variables
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        # Checking if user exist or not
        if user is not None:
            login(request, user)
            return redirect('/')
        # If user password or username is incorrect
        else:
            sweetify.error(request, 'Username or Password is incorrect')

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
    
    # Handle user delete
    if request.method == 'POST':
        if "deleteUser" in request.POST:
            if "user" in request.POST:
                username = request.POST.get("user")
                user = User.objects.get(username=username)
                user.delete()
                messages.success(request, 'User deleted successfully')
                return redirect('adminDashboard')


    # Set the number of items per page
    items_per_page = 4  

    # Get the current page number from the request's GET parameters
    page = request.GET.get('page', 1)

    # Create a Paginator object
    paginator = Paginator(allVerifiedUsers, items_per_page)

    try:
        # Get the current page
        allVerifiedUsers = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, delivering the first page
        allVerifiedUsers = paginator.page(1)
    except EmptyPage:
        # If page is out of range, delivering the last page of results
        allVerifiedUsers = paginator.page(paginator.num_pages)
    
    context = {
        'allVerifiedUsers': allVerifiedUsers,
        'totalVerifiedUsers' : totalVerifiedUsers,
        'totalUsersWhoRequestForOwner' : totalUsersWhoRequestForOwner,  
    }
    return render(request, 'Admin/adminDashboard.html', context)

@login_required(login_url='signin')
@user_passes_test(is_superuser)
def pendingRequests(request):
    # Filtering
    allUsersWhoRequestForOwner = User.objects.filter(groups__isnull=True).exclude(is_superuser=True)
    
    # Pagination
    
    # Set the number of items per page
    items_per_page = 4
    
    
    # Get the current page number from the request's GET parameters
    page = request.GET.get('page', 1)

    # Create a Paginator object
    paginator = Paginator(allUsersWhoRequestForOwner, items_per_page)

    try:
        # Get the current page
        allUsersWhoRequestForOwner = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, delivering the first page
        allUsersWhoRequestForOwner = paginator.page(1)
    except EmptyPage:
        # If page is out of range, delivering the last page of results
        allUsersWhoRequestForOwner = paginator.page(paginator.num_pages)
    
    
    # Handeling approvals
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
                
                # SUCCESS MESSAGE
                messages.success(request, 'User approved successfully')
                
                return redirect('pendingRequests')

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
                # REJECT MESSAGE
                messages.error(request, 'User rejected')
                return redirect('pendingRequests')
    context = {
        'allUsersWhoRequestForOwner' : allUsersWhoRequestForOwner
    }
    
    return render(request, 'Admin/pendingRequests.html', context)


# Owner and Tenant Management view

# Check if user is owner or not
def is_owner(user):
    return user.groups.filter(name='owner').exists()

# Check if user is tenant or not
def is_tenant(user):
    return user.groups.filter(name='tenant').exists()

# Check if user is tenant or owner
def is_tenant_or_owner(user):
    return user.is_authenticated and user.groups.filter(name='tenant').exists() or user.groups.filter(name='owner').exists()

         
# Tenant dashboard management
@login_required(login_url='signin')
@user_passes_test(is_tenant_or_owner)
def dashboard(request):    
    return render(request, 'Users profile/dashboard.html')


# Tenant dashboard management
@login_required(login_url='signin')
@user_passes_test(is_tenant_or_owner)
def editProfile(request):
    # IF form is submitted
    if request.method == 'POST':
        if "user" in request.POST:
                username = request.POST.get('user')
                user = User.objects.get(username=username)
                
        if "update" in request.POST:
            # UPDATING USER MODEL
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.save()
            
            # UPDATING UserAdditionalDetail MODEL
            additionalDetail = user.useradditionaldetail
            additionalDetail.contact_number = request.POST.get('contact')
            additionalDetail.save()
            messages.success(request, 'Profile Updated')           
        
        if "saveImage" in request.POST:
            # Saving user New profile
            user_profile = UserProfilePicture.objects.get(user=user)
            user_profile.image = request.FILES['img']
            user_profile.save()
            messages.success(request, 'Profile Picture Updated')
        
        if "deleteImage" in request.POST:
            user_profile = UserProfilePicture.objects.get(user=user)
            user_profile.delete()
            # Saving user default profile
            user_default_profile_picture = UserProfilePicture(user=user)
            user_default_profile_picture.save()
            messages.success(request, 'Profile Picture updated.')
            
        return redirect('editProfile')                
                
    return render(request, 'Users profile/editProfile.html')

# Change password logic
@login_required(login_url='signin')
@user_passes_test(is_tenant_or_owner)
def changePassword(request):
    # IF form is submitted
    if request.method == 'POST':
        if "user" in request.POST:
                username = request.POST.get('user')
                user = User.objects.get(username=username)
        
        # After user submit the form getting the passwords 
        if "changePassword" in request.POST:
            current_password = request.POST.get('currentPassword')
            new_password = request.POST.get('password1')
            confirm_new_password = request.POST.get('password2')
            
            # If current password is incorrect display error message
            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            
            # If current password is correct:
            else:
                # Check if new password and cormform password is correct
                # If not correct display error message
                if new_password != confirm_new_password:
                    messages.error(request, 'New password and confirm password do not match.')
                    
                # If correct change the password with new password 
                else:
                    # Change the user's password
                    request.user.set_password(new_password)
                    request.user.save()
                    messages.success(request, 'Password Changed')
                    # Updating the user's session to prevent logout
                    update_session_auth_hash(request, request.user)
                    
    return render(request, 'Users profile/changePassword.html')