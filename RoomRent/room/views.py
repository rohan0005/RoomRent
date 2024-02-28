from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from .models import *
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger #for pagination 
from datetime import datetime
from django.http import HttpResponse




# Check if user is owner or not
def is_owner(user):
    return user.groups.filter(name='owner').exists()

# Check if user is tenant or not
def is_tenant(user):
    return user.groups.filter(name='tenant').exists()

# Check if user is tenant or owner
def is_tenant_or_owner(user):
    return user.is_authenticated and user.groups.filter(name='tenant').exists() or user.groups.filter(name='owner').exists()


@user_passes_test(is_owner)
def listing(request):
    step = "1"
    with transaction.atomic():
        if request.method == 'POST' and "step1" in request.POST:
            # STEP 1: Enter your room title, description and address
            roomTitle = request.POST.get('roomTitle')
            roomDescription = request.POST.get('roomDescription')
            roomAddress = request.POST.get('roomAddress')
            detailedRoomAddress = request.POST.get('detailedRoomAddress')

            # STEP 2: Enter Room details
            floor = request.POST.get('floor')
            numberOfBathroom = request.POST.get('numberOfBathroom')
            flatNum = request.POST.get('flat')
            flatType = request.POST.get('flatType')
            parking = request.POST.get('parking')
        
            flat = flatNum +" "+ flatType
            print(floor, numberOfBathroom, flat, flatType, parking)
        

            # STEP 3: Choose Amenities
            amenities = []
            # Check if each checkbox is checked and add its value to the amenities list
            if "amenity1" in request.POST:
                amenities.append(request.POST["amenity1"])
            if "amenity2" in request.POST:
                amenities.append(request.POST["amenity2"])
            if "amenity3" in request.POST:
                amenities.append(request.POST["amenity3"])
            if "amenity4" in request.POST:
                amenities.append(request.POST["amenity4"])
            if "amenity5" in request.POST:
                amenities.append(request.POST["amenity5"])
            if "amenity6" in request.POST:
                amenities.append(request.POST["amenity6"])
            if "amenity7" in request.POST:
                amenities.append(request.POST["amenity7"])
            if "amenity8" in request.POST:
                amenities.append(request.POST["amenity8"])
            if "amenity9" in request.POST:
                amenities.append(request.POST["amenity9"])
                
                
            # STEP 4: Add Rules for your room
            rules_string = request.POST.get('rules')
            
            # Split the rules string into individual rules and append them to the list
            rules = rules_string.split(", ")

            # STEP 5: Utility Information
            electricity=request.POST.get('Electricity')
            electricity ='{:.2f}'.format(float(electricity))
            
            water=request.POST.get('Water')
            water ='{:.2f}'.format(float(water))
            
            trash=request.POST.get('Trash')
            trash ='{:.2f}'.format(float(trash))
            
            rent=request.POST.get('Rent')
            rent ='{:.2f}'.format(float(rent))
            
            
            # Save the data in the database
            room = Room(
                user=request.user, 
                roomTitle=roomTitle, 
                electricity=electricity,
                water=water,
                trash=trash,
                rent=rent,
                roomDescription=roomDescription, 
                roomAddress=roomAddress, 
                detailedRoomAddress=detailedRoomAddress,
                floor=floor, 
                flat=flat, 
                numberOfBathroom=numberOfBathroom , 
                parking=parking, 
                rules=rules, 
                amenities=amenities
            )
            room.save()

            # Step 6: Image handel
            # Handle room images
            room_images = request.FILES.getlist('roomImage')
            for image in room_images:
                new_room_image = RoomImage.objects.create(room=room, image=image)

            # Handle room documents
            room_documents = request.FILES.getlist('roomDocument')
            for document in room_documents:
                new_room_document = RoomDocument.objects.create(room=room, document=document)
                
            messages.success(request, "Your room has been submitted for verification. Thank you!")
            
    if "close" in request.POST:
        return redirect('listing')


    context ={
        'step': step,
    }
    
    return render(request, 'Rooms/listingPage.html', context)


# return superuser
def is_superuser(user):
    return user.is_superuser

# If user is admin
@login_required(login_url='signin')
@user_passes_test(is_superuser)
def pendingRooms(request):
    allPendingRooms = Room.objects.filter(approved=False)
    
    # Handeling room approvals
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        print("ROOM ID IS:", room_id)
        room = get_object_or_404(Room, pk=room_id)
        if "approve" in request.POST:
            # Approving room
            room.listed_date = timezone.now()  # Update the listed_date to the current time
            room.approved = True # set the approverd to True
            room.save()
            messages.success(request, "Room approved")
            return redirect('pendingRooms')

        
        # IF rejected room
        else:
            room.delete()
            messages.error(request, "Room rejected")
            return redirect('pendingRooms')
    
    
    # Pagination
    # Set the number of items per page
    items_per_page = 4  

    # Get the current page number from the request's GET parameters
    page = request.GET.get('page', 1)

    # Create a Paginator object
    paginator = Paginator(allPendingRooms, items_per_page)

    try:
        # Get the current page
        allPendingRooms = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, delivering the first page
        allPendingRooms = paginator.page(1)
    except EmptyPage:
        # If page is out of range, delivering the last page of results
        allPendingRooms = paginator.page(paginator.num_pages)
    

    context = {
        'allPendingRooms': allPendingRooms,
    }
    return render(request, 'Admin/pendingRooms.html', context)

# owner can views their rooms here 
def myRoom(request):
    
    # Get the room which have approved = True in database
    allApprovedRooms = Room.objects.filter(approved=True)
    currentUser = request.user
    
    # Get the room details which user has booked 
    joinedRoomDetails = BookRoom.objects.filter(user=currentUser)
    
    # Filter BookRoom instances based on the current user and the 'joined' field being False
    notJoinedAndPending = BookRoom.objects.filter(user=currentUser, joined=False)
    
    
    if request.method == 'POST':
        # Retrieve the data from the request.POST dictionary
        pageName = request.POST.get('page')
            
        return redirect("roomMoreDetails", room_id = pageName)
    
    context = {
        'allApprovedRooms': allApprovedRooms,
        'notJoinedAndPending' : notJoinedAndPending,
        'joinedRoomDetails' : joinedRoomDetails,
        
    }

    return render(request, 'Rooms/myRoom.html', context)


# This is an explore room page
def room(request):
    
    # All the approved rooms:
    allApprovedRooms = Room.objects.filter(approved=True, isAvailable = True, isBooked = False)
    
    context = {
        'allApprovedRooms': allApprovedRooms
    }
    return render(request, 'Rooms/exploreRoom.html', context)

# import re
def roomMoreDetails(request, room_id):
    
    currentUser = request.user # get the current user
    hasBookedRoom = BookRoom.objects.filter(user=currentUser).exists() # checkk if this user has booked the room

    roomDetail = Room.objects.get(id=room_id)
    
    roomRule = roomDetail.rules  # Assuming 'details' is the field containing the string data

    # Use regular expressions to extract individual details
    roomRules = [rules.strip("' ") for rules in roomRule.strip("[]").split("', '")]
    
    
    amenities = roomDetail.amenities
    
    amenities = [amenities.strip("' ") for amenities in amenities.strip("[]").split("', '")]

    # booking logic
    if request.method == "POST":
        with transaction.atomic():
            #Get move in date and change the format 
            requestedMoveInDate = request.POST.get("moveInDate") 
            parsed_date = datetime.strptime(requestedMoveInDate, '%m/%d/%Y')
            moveInDate = parsed_date.strftime('%Y-%m-%d')

            # Get the room id
            roomID = request.POST.get("room_id")
            room = get_object_or_404(Room, pk=roomID)

            # Get the user id who is booking the room
            userId = request.user.id
            user = get_object_or_404(User, pk=userId)
            
            # Update the room model
            room.isAvailable = False # set the approverd to False
            
            room.isBooked = True # set the booking to True
            room.save() # Update the room details

            # Save the booking
            booking = BookRoom.objects.create(room=room, moveInDate=moveInDate , user=user)
            booking.save()
            
            # return redirect('roomMoreDetails', room_id=room_id )
            # messages.success(request, "Room Booked.")
            
            context = {
                    'roomID': roomID, 
            }
            
            # Construct an HTTP response with the context data
            response_content = f"Room has been booked. Please wait before the owner approves you. View your booking details at <a href='/room/details/{context['roomID']}'>Booking Details</a>"
            response = HttpResponse(response_content)

            return response
        
    
    context = {
        'roomDetail': roomDetail,
        'roomRules' : roomRules,
        'amenities' : amenities,
        'hasBookedRoom' : hasBookedRoom,
    }
    
    return render(request, 'Rooms/roomMoreDetails.html', context)

# hTTP RESPONSE PAGE MA JANE BOOK VAYA SEEE

# View Booking as Owner
def booking(request):
    return render(request, 'Rooms/booking.html')
