from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from .models import *
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger #for pagination 



# Check if user is owner or not
def is_owner(user):
    return user.groups.filter(name='owner').exists()


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

