from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages

# SIGNUP UP NEW USERS
def SignupUser(request):
    return render(request,'Authentication/signin and signup/signup.html')

# SIGNIN USERS
def SigninUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        # Checking if user exist or not
        if user is not None:
            login(request, user)
            # redirecting to home page if user exist
            return redirect('/')
        else:
            messages.info(request, 'Username or Password is incorrect')

    return render(request,'Authentication/signin and signup/signin.html')

# SIGNOUT USER
def signoutUser(request):
    logout(request)
    return redirect('signin')