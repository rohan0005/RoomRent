from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash # for authentication
from django.contrib import messages
from .models import *
from room.models import Room, BookRoom
from .forms import *
from django.db import transaction
from django.contrib.auth.models import Group, User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger #for pagination 
from django.core.mail import send_mail, EmailMessage # For sending email notifications
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from .tokens import generate_token
from django.conf import settings
from userManagement.checkUserGroup import *
from django.http import Http404


import re

import sweetify

# Main logis are written in the views.py

# SIGNUP UP NEW USERS
def SignupUser(request):
    try:
        
        form = CreateUserForm()
        if request.method == 'POST':
            # try:
            form = CreateUserForm(request.POST, request.FILES) # Get the form data and if user uploads files get files too 
            if form.is_valid():
                if User.objects.filter(email=request.POST.get('email')).exists():
                    sweetify.error(request, "Email already registered!", button='Ok', timer=0)
                    return redirect('signup')
                # Get the username
                username = form.cleaned_data.get('username')
                if 'contact' in request.POST:
                    contact_number = request.POST.get('contact')
                if not re.match(r'^(98|97)\d{8}$', contact_number):
                    sweetify.error(request,"Invalid contact number", button='Ok', timer=0)                  
                    return redirect('signup')

                with transaction.atomic():
                    user = form.save(commit=False)
                    user.is_active = False
                    user.save()
                    
                    
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
                    
                    # If user choose to become tenant then adding them to tenant group
                    else:
                        group, created = Group.objects.get_or_create(name='tenant')
                        user.groups.add(group)
                    
                    # SEND MAIL
                    # Send welcome email
                    subject = "Welcome to RoomRent Website"
                    message = f"Hello {user.username}!\n\nThank you for registering on our website. Please confirm your email address to activate your account.\n\nRegards,\nRoomRent"
                    from_email = settings.EMAIL_HOST_USER
                    to_list = [user.email]
                    # send_mail(subject, message, from_email, to_list, fail_silently=True)
                    
                    # Send email confirmation link
                    current_site = get_current_site(request)
                    email_subject = "Confirm Your Email Address"
                    message2 = render_to_string('Users profile/email_confirmation.html', {
                    'name': user.username,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': generate_token.make_token(user)
                    })
                    email = EmailMessage(
                    email_subject,
                    message2,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    )
                    send_mail(email_subject, message2, from_email, to_list, fail_silently=True)
                    sweetify.success(request, "Please check your email to confirm your email address and activate your account.", button='Ok', timer=0)
                    return redirect('signin')
                    
                return redirect('signin') # After creating the user redirect to the signin page
            # If form is not valid
            elif not form.is_valid():
                errorMessage = next(iter(form.errors.values()))[0]     # Retrieving the first error message from the form errors
                sweetify.error(request, errorMessage, button='Ok', timer=0)

        return render(request,'Authentication/signin and signup/signup.html')
    except:
        sweetify.error(request, 'Something went wrong!',   button='Ok', timer=0)
        return redirect('signup')

# SIGNIN USERS
def SigninUser(request):
    try:
        
        if request.method == 'POST':
            # request and assign the user name and password to the variables
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            
            # Checking if user exist or not
            if user is not None:
                if user.is_superuser:
                    login(request, user)
                    sweetify.success(request, 'Successfully Signed In', button='Ok', timer=0)
                    return redirect('adminDashboard')
                    
                elif user.useradditionaldetail.has_blocked == True: # if user is blocked then dont give access to signin
                    logout(request)
                    sweetify.error(request, 'Your account is blocked. Please contact to admin.', button='Ok', timer=0)
                    return redirect('signin')
                else:
                    login(request, user)
                    sweetify.success(request, 'Successfully Signed In', button='Ok', timer=0)
                    return redirect('index')
            # If user password or username is incorrect
            else:
                sweetify.error(request, 'Username or Password is incorrect', button='Ok', timer=0)
        return render(request, 'Authentication/signin and signup/signin.html')
    except:
        sweetify.error(request, 'Something went wrong!',   button='Ok', timer=0)
        return redirect('signin')
        

# SIGNOUT USER
def signoutUser(request):
    try:
        logout(request)
        sweetify.success(request, 'Successfully Signed Out', button='Ok', timer=0)
        return redirect('signin')
    except:
        sweetify.error(request, 'Something went wrong!',   button='Ok', timer=0)
        return redirect('signin')

# return superuser
def is_superuser(user):
    return user.is_superuser


# Admin Pages
@login_required(login_url='signin')
@user_passes_test(is_superuser)
def adminDashboard(request):
    try:
    
        allVerifiedUsers = User.objects.filter(groups__name__in=['owner', 'tenant'])
        totalVerifiedUsers = User.objects.filter(groups__name__in=['owner', 'tenant']).count()       
        totalUsersWhoRequestForOwner = User.objects.filter(groups__isnull=True).exclude(is_superuser=True).count()
        totalPendingRooms = Room.objects.filter(approved=False).count()

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
            'totalPendingRooms' : totalPendingRooms,
        }
        return render(request, 'Admin/adminDashboard.html', context)
    except:
        sweetify.error(request, 'Something went wrong!',   button='Ok', timer=0)
        return redirect('index')
        
        
# PENDING USER REQUEST
@login_required(login_url='signin')
@user_passes_test(is_superuser)
def pendingRequests(request):
    try:
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
        context = {
            'allUsersWhoRequestForOwner' : allUsersWhoRequestForOwner
        }
        return render(request, 'Admin/pendingRequests.html', context)
    except:
        sweetify.error(request, 'Something went wrong!',   button='Ok', timer=0)
        return redirect('adminDashboard')



@login_required(login_url='signin')
@user_passes_test(is_superuser)
def userMoreDetail(request, user_id):
    try:
        userData = get_object_or_404(User, pk=user_id)
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
                    sweetify.success(request, 'User approved successfully', button='Ok', timer=0)
                    
                    return redirect('pendingRequests')
                
            elif "block" in request.POST:
                username = request.POST.get("user")
                user = User.objects.get(username=username)
                user_email = user.email
                # Sending mail after user is approved
                send_mail(
                "Account Blocked",
                "Your account has been Blocked in RoomRent website. Please Contact to admin.",
                "room.rent.webapp@gmail.com",
                [user_email],
                fail_silently=False,
                )
                userDetail = UserAdditionalDetail.objects.get(user=user)
                userDetail.has_blocked = True
                userDetail.save()
                sweetify.success(request, 'User Blocked successfully', button='Ok', timer=0)
            
            elif "unblock" in request.POST:
                username = request.POST.get("user")
                user = User.objects.get(username=username)
                user_email = user.email
                # Sending mail after user is approved
                send_mail(
                "Account Unblocked",
                "Your account has been Unblocked in RoomRent website. You can now signin.",
                "room.rent.webapp@gmail.com",
                [user_email],
                fail_silently=False,
                )
                userDetail = UserAdditionalDetail.objects.get(user=user)
                userDetail.has_blocked = False
                userDetail.save()
                sweetify.success(request, 'User Unblocked successfully', button='Ok', timer=0)
            
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
                    sweetify.error(request, 'User rejected', button='Ok', timer=0)
                    return redirect('pendingRequests')
    
        context = {
            "user" : userData
        }
        return render(request, 'Admin/userDetail.html', context)
    
    except Http404 as e:
        print("e",e)
        return render(request, '505_404.html')
    
    except Exception as e:
        print("e", e)
        sweetify.error(request, 'Something went wrong!',   button='Ok', timer=0)
        return redirect('adminDashboard')
        

# Tenant dashboard management
@login_required(login_url='signin')
@user_passes_test(is_tenant_or_owner)
def editProfile(request):
    try:
        # IF form is submitted
        if request.method == 'POST':
            if "user" in request.POST:
                    username = request.POST.get('user')
                    user = User.objects.get(username=username)
                    
            if "update" in request.POST:
                # UPDATING USER MODEL
                user.first_name = request.POST.get('first_name')
                user.last_name = request.POST.get('last_name')
                user.save()
                
                # UPDATING UserAdditionalDetail MODEL
                additionalDetail = user.useradditionaldetail

                if 'contact' in request.POST:
                    contact_number = request.POST.get('contact')
                    if not re.match(r'^(98|97)\d{8}$', contact_number):
                        sweetify.error(request,"Invalid contact number", button='Ok', timer=0)                  
                        return redirect('editProfile')                

                    else:
                        additionalDetail.contact_number = request.POST.get('contact')
                        additionalDetail.save()
                        sweetify.success(request, 'Profile Updated', button='Ok', timer=0)           
            
            if "saveImage" in request.POST:
                if request.FILES:
                    # Saving user New profile
                    user_profile = UserProfilePicture.objects.get(user=user)
                    user_profile.image = request.FILES['img']
                    user_profile.save()
                    sweetify.success(request, 'Profile Picture Updated', button='Ok', timer=0)
                else:
                    sweetify.warning(request, 'No image selected', button='Ok', timer=0)
            
            if "deleteImage" in request.POST:
                user_profile = UserProfilePicture.objects.get(user=user)
                user_profile.delete()
                # Saving user default profile
                user_default_profile_picture = UserProfilePicture(user=user)
                user_default_profile_picture.save()
                sweetify.success(request, 'Profile Picture updated.', button='Ok', timer=0)
                
            return redirect('editProfile')                
        return render(request, 'Users profile/editProfile.html')
    except:
        sweetify.error(request, 'Something went wrong!',   button='Ok', timer=0)          
        return redirect('index')
        
        
# Change password logic
@login_required(login_url='signin')
@user_passes_test(is_tenant_or_owner)
def changePassword(request):
    try:
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
                    sweetify.error(request, 'Current password is incorrect.', button='Ok', timer=0)
                
                # If current password is correct:
                else:
                    # Check if new password and cormform password is correct
                    # If not correct display error message
                    if new_password != confirm_new_password:
                        sweetify.error(request, 'New password and confirm password do not match.', button='Ok', timer=0)
                        
                    # If correct change the password with new password 
                    else:
                        # Change the user's password
                        request.user.set_password(new_password)
                        request.user.save()
                        sweetify.success(request, 'Password Changed', button='Ok', timer=0)
                        # Updating the user's session to prevent logout
                        update_session_auth_hash(request, request.user)
        return render(request, 'Users profile/changePassword.html')
    except:
        sweetify.error(request, 'Something went wrong!',   button='Ok', timer=0)         
        return redirect('index')


def activate(request, uidb64, token):
    try:
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))  
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            target_groups = ['tenant']
            if user.groups.filter(name__in=target_groups).exists():
                sweetify.success(request, "Account activated successfully.!", button='Ok', timer=0)
            else:
                sweetify.success(request, "Account activated successfully. Please wait for the admin approval.", button='Ok', timer=0)
            return redirect('signin')
        else:
            sweetify.error(request, "Something went erong while activating your account", button='Ok', timer=0)
            return redirect('signin')
    except:
        sweetify.error(request, 'Something went wrong!',   button='Ok', timer=0)
        return redirect('index')
