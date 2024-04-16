from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from .models import *
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger #for pagination 
from datetime import datetime
from django.http import HttpResponse
from django.db.models import Q
from payment.models import *
from django.core.mail import send_mail # For sending email notifications
from django.http import Http404
import sweetify
from userManagement.checkUserGroup import *



@login_required(login_url='signin')
@user_passes_test(is_owner)
def listing(request):
    try:
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
                    
                sweetify.success(request, "Your room has been submitted for verification. Thank you!",  button='Ok', timer=0)

        context ={
            'step': step,
        }
        return render(request, 'Rooms/listingPage.html', context)
    except:
        sweetify.error(request, 'Something went wrong!',   button='Ok', timer=0)
        return redirect('index')


# return superuser
def is_superuser(user):
    return user.is_superuser

# If user is admin and Pending rooms
@login_required(login_url='signin')
@user_passes_test(is_superuser)
def pendingRooms(request):
    try:
        allPendingRooms = Room.objects.filter(approved=False)
        
        # Handeling room approvals
        if request.method == 'POST':
            room_id = request.POST.get('room_id')
            user = request.POST.get("user")
            userForEmail = User.objects.get(pk=user)
            user_email = userForEmail.email
            room = get_object_or_404(Room, pk=room_id)
            if "approve" in request.POST:
                # Approving room
                room.listed_date = timezone.now()  # Update the listed_date to the current time
                room.approved = True # set the approverd to True
                room.save()
                # Sending mail after room booking is rejected
                send_mail(
                "Room Listing Approved",
                f"We are pleased to inform you that your request to list your room has been approved. Your room is now listed on our platform and visible to all users. Thank you for choosing our platform",
                "room.rent.webapp@gmail.com",
                [user_email],
                fail_silently=False,
                )
                sweetify.success(request, "Room approved",  button='Ok', timer=0)
                return redirect('pendingRooms')

            
            # IF rejected room
            else:
                send_mail(
                "Room Listing Rejected",
                f"We regret to inform you that your request to list your room has been rejected. Thank you for considering our platform. Thank you for considering our platform.",
                "room.rent.webapp@gmail.com",
                [user_email],
                fail_silently=False,
                )
                room.delete()
                sweetify.error(request, "Room rejected",  button='Ok', timer=0)
                return redirect('pendingRooms')
            
            
            
                user = request.POST.get("user")
                roomId = request.POST.get('roomId')
                
                userForEmail = User.objects.get(pk=user)
                
                user_email = userForEmail.email
                
                
                
                booking = BookRoom.objects.get(user=user, id=roomId)
                room_id = booking.room.id
                room = Room.objects.get(id=room_id)
                
                # Sending mail after room booking is rejected
                send_mail(
                "Room joining request Rejected",
                f"Your request for joining {room.roomTitle} is rejected",
                "room.rent.webapp@gmail.com",
                [user_email],
                fail_silently=False,
                )
        
        
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
    except:
        sweetify.error(request, 'Something went wrong!',   button='Ok', timer=0)
        return redirect('index')
    
# owner can views their rooms here 
@login_required(login_url='signin')
@user_passes_test(is_tenant_or_owner)
def myRoom(request):
    try:
        
        step = None
        currentUser = request.user
        # Get the room which have approved = True in database
        allApprovedRooms = Room.objects.filter(user=currentUser, approved=True)
        allRooms = Room.objects.filter(user=currentUser)
        
        bookingLog = TenantBookingLog.objects.filter(user=currentUser)
        
        bookedRoomDetails = BookRoom.objects.filter(user=currentUser)

        
        # Filter BookRoom instances based on the current user and the 'joined' field being False
        bookingDetailsWithJoinedFalse = BookRoom.objects.filter(user=currentUser, joined=False)
        if bookingDetailsWithJoinedFalse.exists() and bookingDetailsWithJoinedFalse.count() == bookingDetailsWithJoinedFalse.filter(joined=False).count():
            notJoinedAndPending = True  #All objects have joined=False
        else:
            notJoinedAndPending = False #There are objects with joined=True or the queryset is empty
        
        isjoined = BookRoom.objects.filter(joined=True)
        
        hasMoveOutDate = BookRoom.objects.filter(joined=True, moveOutDate__isnull=False).values_list('room', flat=True) #it returns a list of values from the room field of the queryset in a flat format, allowing us to easily extract and manipulate these values
        
        if request.method == 'POST':
            # Retrieve the data from the request.POST dictionary
            if 'page' in request.POST:
                pageName = request.POST.get('page')
                return redirect("roomMoreDetails", room_id = pageName)
        
        if request.method == 'POST':
            if 'myroom' in request.POST:
                step = 'myroom'
            elif 'bookinglog' in request.POST:
                step = 'bookinglog'

                

        context = {
            'allApprovedRooms': allApprovedRooms,
            'notJoinedAndPending' : notJoinedAndPending,
            'bookedRoomDetails' : bookedRoomDetails,
            'isjoined' : isjoined,
            'hasMoveOutDate' : hasMoveOutDate,
            'allRooms' : allRooms,
            'step' : step,
            'bookingLog' : bookingLog,
            
        }
        return render(request, 'Rooms/myRoom.html', context)
    except:
        sweetify.error(request, 'Something went wrong!',   button='Ok', timer=0)    
        return redirect('index')


# This is an explore room page
def room(request):
    try:
    
        # All the approved rooms:
        allApprovedRooms = Room.objects.filter(approved=True, isAvailable = True) # multiple user can book the same room
        
        search = request.GET.get('search_query')
        # Handle filter options
        flat = request.GET.get('Flat')
        parking = request.GET.get('parking')
        floor = request.GET.get('floor')
        rent = request.GET.get('rent')
        
        
        if search:
            allApprovedRooms = allApprovedRooms.filter(Q(roomTitle__icontains=search) | Q(roomAddress__icontains=search))
        else:
            allApprovedRooms = Room.objects.filter(approved=True, isAvailable = True) # multiple user can book the same room
            
        if flat is not None:
            allApprovedRooms = allApprovedRooms.filter(Q(flat__icontains=flat))
        
        if parking is not None:
            allApprovedRooms = allApprovedRooms.filter(Q(parking__icontains=parking))
            
        if floor is not None:
            allApprovedRooms = allApprovedRooms.filter(Q(floor__icontains=floor))
            
        if rent and not rent == "":
            allApprovedRooms = allApprovedRooms.filter(rent__lte=rent) # Filter rooms where rent is less than or equal to the specified value. lte - comparison filter that stands for -less than or equal to
            print(rent)
        
        # Pagination
        paginator = Paginator(allApprovedRooms, 3)  # Show 3 rooms per page
        page_number = request.GET.get('page')
        try:
            allApprovedRooms = paginator.page(page_number)
        except PageNotAnInteger:
            allApprovedRooms = paginator.page(1)
        except EmptyPage:
            allApprovedRooms = paginator.page(paginator.num_pages)

            
        context = {
            'allApprovedRooms': allApprovedRooms,
            'search': search,
            'flat' : flat,
            'parking' : parking,
            'floor' : floor,
            'rent' : rent,
        }
        return render(request, 'Rooms/exploreRoom.html', context)
    except:
        sweetify.error(request, 'Something went wrong!',   button='Ok', timer=0)
        return redirect('index')
    
@login_required
def roomMoreDetails(request, room_id):
    try:
        room_instance = get_object_or_404(Room, pk=room_id)
        bookedRoom = BookRoom.objects.filter(room=room_instance, joined = True, user = request.user).first()
        print("bookedRoom", bookedRoom)
        # Check if the room is approved by the admin
        if not room_instance.approved:
            # If the room is not approved and the user is not the owner or admin then show 404 page
            if not (request.user.is_superuser or request.user == room_instance.user):
                # raise Http404("Room not found")
              return render(request, '505_404.html')
        elif room_instance.approved == True and room_instance.isAvailable == False:
            if not bookedRoom and room_instance.user != request.user and not request.user.is_superuser:
                return render(request, '505_404.html')
            
            
            # if not(request.user.is_authenticated or request.user == room_instance.user) and bookedRoom is None:
            #     # raise Http404("Room not found")
            #   return render(request, '505_404.html')
            
        room_instance = get_object_or_404(Room, pk=room_id)
        checkRoom = SavedRoom.objects.filter(user=request.user, room=room_instance).exists()
        checkMaintenance= room_instance.isUnderMaintenance
        # Check if the room is saved by the current user
        if request.method == 'POST' and 'saveRoom' in request.POST:
            
            if not checkRoom:
                    SavedRoom.objects.create(user=request.user, room=room_instance)
                    sweetify.success(request, "Room saved successfully!", button='Ok', timer=0)
                    return redirect('roomMoreDetails', room_id=room_id)
            else:
                SavedRoom.objects.filter(user=request.user, room=room_instance).delete()
                sweetify.success(request, "Room removed from saved!", button='Ok', timer=0)
                return redirect('roomMoreDetails', room_id=room_id)
        elif "Checkmaintenance" in request.POST:
            if room_instance.isUnderMaintenance == False:
                room_instance.isUnderMaintenance = True
                room_instance.save()
                sweetify.success(request, "Room status changed to under maintenance.", button='Ok', timer=0)
                return redirect('roomMoreDetails', room_id=room_id)
            else:
                room_instance.isUnderMaintenance = False
                room_instance.save()
                sweetify.success(request, "Room status changed to available for booking.", button='Ok', timer=0)
                return redirect('roomMoreDetails', room_id=room_id)
            
        if request.method == 'POST' and 'RoomIssue' in request.POST:
            RoomIssueFeedback = request.POST.get('RoomIssueFeedback')
            RoomIssueFeedbackMessage = request.POST.get('RoomIssueFeedbackMessage')
            print('RoomIssueFeedback , RoomIssueFeedbackMessage', RoomIssueFeedback, RoomIssueFeedbackMessage)
            RoomIssuesOrMaintenance.objects.create(user=request.user, room=room_instance, type=RoomIssueFeedback, message= RoomIssueFeedbackMessage, status="Pending" )
            sweetify.success(request, "Message has been sent to your room owner.", button='Ok', timer=0)
            return redirect('roomMoreDetails', room_id=room_id)
            
        
        if request.method == 'POST':
            if "updateUtility" in request.POST:
                roomInstance = Room.objects.get(pk=room_id)
                newElectricity = request.POST.get("editElectricity")
                newRent = request.POST.get("rent")
                editWater = request.POST.get("editWater")
                editTrash = request.POST.get("editTrash")
                
                roomInstance.electricity = newElectricity
                roomInstance.water = editWater
                roomInstance.trash = editTrash
                roomInstance.rent = newRent
                roomInstance.save()
                
                sweetify.success(request, "Utility update!", button='Ok', timer=0)
                return redirect("roomMoreDetails", room_id = room_id)
        
            elif "newAmenities" in request.POST:
                        new_amenity = request.POST.get("newAmenitiesName").capitalize()
                        roomInstance = Room.objects.get(pk=room_id)
                        amenities_list = eval(roomInstance.amenities) if roomInstance.amenities else [] # Convert the amenities string to a list
                        amenities_list.append(new_amenity)  # Append the new amenity to the existing list of amenities
                        roomInstance.amenities = str(amenities_list) # save as astring in the database
                        roomInstance.save()
                        sweetify.success(request, "New Amenity Added!", button='Ok', timer=0)
                        return redirect("roomMoreDetails", room_id=room_id)
                    
            elif "deleteAmenities" in request.POST:
                room_instance = get_object_or_404(Room, pk=room_id)
                amenityDelete = request.POST.get('amenity_to_delete')
                
                # Convert the amenities string to a list
                room_instance.amenities = eval(room_instance.amenities)

                if amenityDelete in room_instance.amenities:
                    room_instance.amenities.remove(amenityDelete)
                    # Convert the amenities list back to a string
                    room_instance.amenities = str(room_instance.amenities)
                    room_instance.save()
                    sweetify.success(request, "Amenity Deleted!", button='Ok', timer=0)
                    return redirect("roomMoreDetails", room_id=room_id)
                
            elif "addNewRules" in request.POST:
                room_instance = get_object_or_404(Room, pk=room_id)
                room_instance.rules = []  # Remove all existing rules by assigning an empty list
                room_instance.save()
                
                rules_string = request.POST.get('rules')
                print("rules_stringrules_stringrules_string", rules_string)
                # Split the rules string into individual rules and append them to the list
                newRules = rules_string.split(", ")
                room_instance.rules = newRules
                room_instance.save()
                sweetify.success(request, "New Rules added!", button='Ok', timer=0)
                return redirect("roomMoreDetails", room_id=room_id)
        
        currentUser = request.user # get the current user
        hasJoinedRoom = BookRoom.objects.filter(user=currentUser, joined=True).exists() # Check if user has already joined room
        hasBookedThisRoom = BookRoom.objects.filter(user=currentUser, room=room_id).exists() # check if user has booked this room 
        hasJoinedMyRoom = BookRoom.objects.filter(room=room_id, joined=True).exists()
        # Check if there is a move out date or not
        hasNotMoveOutDate = BookRoom.objects.filter(joined=True, room=room_id, moveOutDate__isnull=True).exists()
        bookedRoomInfo = BookRoom.objects.filter(joined=True, room=room_id)
        feedbacks = RoomFeedbacks.objects.filter(room=room_id)
            
        roomDetail = Room.objects.get(id=room_id)
        isAvailable = Room.objects.filter(id=room_id, isAvailable=True)
        roomRule = roomDetail.rules  # Assuming 'details' is the field containing the string data

        # Using regular expressions to extract
        roomRules = [rules.strip("' ") for rules in roomRule.strip("[]").split("', '")]
        
        isJoinedThisRoom = BookRoom.objects.filter(joined=True, room=room_id) 
        
        amenities = roomDetail.amenities
        
        amenities = [amenities.strip("' ") for amenities in amenities.strip("[]").split("', '")]
        print("amenities", amenities)
        # booking logic
        if request.method == "POST":
            if 'moveout' in request.POST:
                with transaction.atomic():
                    moveOutDate = request.POST.get("moveInOrMoveoutDate")  #get the moveout date
                    parsed_date = datetime.strptime(moveOutDate, '%Y-%m-%d')
                    moveOutDate = timezone.make_aware(parsed_date, timezone.get_current_timezone())
                    BookedRoomDetails = BookRoom.objects.get(user=currentUser, room=room_id)
                    BookedRoomDetails.moveOutDate = moveOutDate
                    userFeedback = request.POST.get("feedback")
                    
                    feedback = request.POST.get("feedback")
                    rating = request.POST.get("hs-ratings-readonly")
                    if feedback == "" and rating == None:
                        pass
                    elif feedback != "" and rating == None:
                        roomDetail.roomfeedbacks_set.create(user=currentUser,feedback=feedback) # save feedback after tenant submit moveout
                    elif feedback == "" and rating != None:
                        roomDetail.roomfeedbacks_set.create(user=currentUser,rating=rating) # save rating after tenant submit moveout
                    elif feedback != "" and rating != None:
                        roomDetail.roomfeedbacks_set.create(user=currentUser,rating=rating, feedback= feedback) # save rating and feedback after tenant submit moveout
                    BookedRoomDetails.save()
                    sweetify.success(request, "Moveout informed", button='Ok', timer=0)
                    return redirect("roomMoreDetails", room_id = room_id)
                
            elif 'removeTenant' in request.POST: # Remove the tenant from this room after moveout is completed
                with transaction.atomic():
                    user = request.POST.get("tenantUser")
                    print("tenantUser:", user)
                    roomId = room_id
                    
                    userForEmail = User.objects.get(pk=user)
                    user_email = userForEmail.email
                    room = Room.objects.get(id=roomId)
                    
                    booking = BookRoom.objects.get(room=roomId, joined=True)
                    roombilling = RoomBilling.objects.get(bookedRoom=booking)
                    
                    depositeAmount = roombilling.deposit
                    
                    fineAmount = request.POST.get("fineAmount")
                    fineReason = request.POST.get("fineReason")
                    
                    if not fineAmount == '' and not fineReason == '':
                        message = f"Dear {userForEmail.username},\n\
                        We have received your move-out request for the room '{room.roomTitle}'. \n\
                        Your deposit refund will be processed shortly.\n\
                        From you deposit amount Rs. {depositeAmount}, we have charged you fine of Rs. {fineAmount} because of the following reason:\n\
                        {fineReason}\n\
                        Regards,\n\
                        [RoomRent]"
                    else:
                        message = f"Dear {userForEmail.username},\n\
                        We have received your move-out request for the room '{room.roomTitle}'. \n\
                        Your deposit refund will be processed shortly.\n\
                        Regards,\n\
                        [RoomRent]"
                        
                    print(message)
                        

                    send_mail(
                    "Tenant Move-Out Completed",
                    message,
                    "room.rent.webapp@gmail.com",
                    [user_email],
                    fail_silently=False,
                    )
                            
                    roomDetail.isAvailable = True
                    roomDetail.isBooked = False
                    roomDetail.save()
                    bookedThisRoom = BookRoom.objects.filter(joined=True, room=room_id).first()
                    billing = RoomBilling.objects.filter(bookedRoom=bookedThisRoom) #Delete the billing model associated with this bookedroom 
                    billing.delete()
                    # EMAIL
                    
                    isJoinedThisRoom.delete()
                    sweetify.success(request, "Tenant Movedout", button='Ok', timer=0)
                return redirect("roomMoreDetails", room_id = room_id)
                    
                
            else:
                with transaction.atomic():
                    #Get move in date and change the format 
                    requestedMoveInDate = request.POST.get("moveInOrMoveoutDate") 
                    parsed_date = datetime.strptime(requestedMoveInDate, '%Y-%m-%d')
                    moveInDate = parsed_date.strftime('%Y-%m-%d')
                    additionalDetail = request.POST.get("additionalDetail") 
                    
                    # Get the room id
                    roomID = request.POST.get("room_id")
                    room = get_object_or_404(Room, pk=roomID)

                    # Get the user id who is booking the room
                    userId = request.user.id
                    user = get_object_or_404(User, pk=userId)
                    
                    room.isBooked = True # set the booking to True
                    room.save() # Update the room details

                    if additionalDetail and additionalDetail != "":
                        # Save the booking
                        booking = BookRoom.objects.create(room=room, moveInDate=moveInDate , user=user, rentBilledDate=moveInDate, additionalDetails = additionalDetail)
                        booking.save()
                    else:
                        # Save the booking
                        booking = BookRoom.objects.create(room=room, moveInDate=moveInDate , user=user, rentBilledDate=moveInDate)
                        booking.save()
                    
                    sweetify.success(request, "Room Booked!", button='Ok', timer=0)
                    
                    return redirect("roomMoreDetails", room_id = room_id)
                    
        
        context = {
            'roomDetail': roomDetail,
            'roomRules' : roomRules,
            'amenities' : amenities,
            'isJoinedThisRoom' : isJoinedThisRoom,
            'hasJoinedRoom' : hasJoinedRoom,
            'hasBookedThisRoom' : hasBookedThisRoom,
            'hasJoinedMyRoom' : hasJoinedMyRoom,
            'hasNotMoveOutDate' : hasNotMoveOutDate,
            'feedbacks' : feedbacks,
            'bookedRoomInfo' : bookedRoomInfo,
            'checkRoom' : checkRoom,
            'checkMaintenance': checkMaintenance
        }
        return render(request, 'Rooms/roomMoreDetails.html', context)
    except Http404 as e:
        return render(request, '505_404.html')
    
    except Exception as e:
        print("e : ",e)
        sweetify.error(request, 'Something went wrong!',   button='Ok', timer=0)
        return redirect('index')

# View Bookings as Owner
@user_passes_test(is_owner)
def viewBooking(request):
    try:
        currentUser = request.user # Get the current user
        bookingLog = TenantBookingLog.objects.filter(user=currentUser)
        step = None
        # Get rooms uploaded by the current user
        roomsUploadedByUser = Room.objects.filter(user=currentUser)
        
        canceledBookingDetails = []
        
        for cancelRoom in roomsUploadedByUser:
            canceledBooking = OwnerBookingLog.objects.filter(room=cancelRoom)
            canceledBookingDetails.extend(canceledBooking)
        
        # Handle Pending or cancel page
        if request.method == 'POST':
            if 'pendingBookings' in request.POST:
                step = "pendingBookings"
                print("pendingBookings")
            if 'canceledBookings' in request.POST:
                step = "canceledBookings"
                print("canceledBookings")
        
        # if user accept the booking
        if request.method == 'POST' and "accept" in request.POST:
            with transaction.atomic():
                user = request.POST.get("user")
                roomId = request.POST.get('roomId')
                print("roomID", roomId)
                booking = BookRoom.objects.get(user=user, id=roomId)
                room_id = booking.room.id
                roomInstance = Room.objects.get(id=room_id)

                #send mail
                userForEmail = User.objects.get(pk=user)
                user_email = userForEmail.email
                
                # Sending mail after room booking is rejected
                send_mail(
                "Booking accepted",
                f"Your Booking for joining {roomInstance.roomTitle} is accepted",
                "room.rent.webapp@gmail.com",
                [user_email],
                fail_silently=False,
                )

                # Retrieve the BookRoom instance based on the user and room
                booking = BookRoom.objects.filter(user=user, id=roomId).first()
                if booking:
                    room = booking.room
                    room.isAvailable = False
                    room.save()
                    # Update the 'joined' attribute to True
                    booking.joined = True
                    booking.save()  # Save the changes
                    billing = RoomBilling.objects.create(bookedRoom=booking) # create the billing model for the joined user
                    billing.save()
                    
                #  UPDATE THE RENT BILLING TO NEXT MONTH AFTER ACCEPTING THE BOOKING
                billing = RoomBilling.objects.filter(bookedRoom=booking, status="pending").exclude(id=None).first() #get the instance of RoomBilling
                if billing and booking.moveInDate == booking.rentBilledDate:
                    move_in_date = booking.rentBilledDate
                    print("move_in_date", move_in_date)
                    try:
                        next_month_date = move_in_date.replace(month=move_in_date.month + 1)
                        booking.rentBilledDate = next_month_date
                        booking.save()
                    except ValueError:
                        next_month_date = move_in_date.replace(year=move_in_date.year + 1, month = 1)  #change the year if month is january
                        booking.rentBilledDate = next_month_date
                        booking.save()
                    
                    
                    
                print("USERNAME IS  : ", user)
                allBookingMadeByUser = BookRoom.objects.filter(user=user, joined = False)
                user = User.objects.get(pk=user)
                if allBookingMadeByUser:
                    for allBooking in allBookingMadeByUser:
                        room = allBooking.room
                        date = allBooking.bookingDate
                        bookinglog = TenantBookingLog.objects.create(user=user, room=room, bookingDate= date, status = "Cancelled After joining")
                        bookinglog.save() # Save the BookingLog 
                        
                        canceledBookingDetails = OwnerBookingLog.objects.create(user=user, room=room, bookingDate= date, canceledDate= timezone.now(),status = "Cancelled After joining")
                        canceledBookingDetails.save() # Save the canceled Bookings
                
                #Remove remaining bookings for the same user and room
                remainingBookings = BookRoom.objects.filter(
                    ~Q(id=booking.id),  # Exclude the accepted booking
                    user=user
                )
                
                # Remove remaining bookings for the same user and not joined
                remainingBookingsForUser = BookRoom.objects.filter(
                    ~Q(id=booking.id),  # Exclude the accepted booking
                    user=user,
                    joined=False
                )
                
                # Remove remaining bookings for the same room and not joined
                remainingBookingsForRoom = BookRoom.objects.filter(
                    ~Q(id=booking.id),  # Exclude the accepted booking
                    room=room,
                    joined=False
                )
                
                remainingBookingsForUser.delete() #Remaining bookings for user to be deleted:
                remainingBookingsForRoom.delete() #Remaining bookings for room to be deleted:

                sweetify.success(request, "Booking approved", button='Ok', timer=0)
                return redirect("viewBooking")
    
        elif request.method == 'POST' and "reject" in request.POST:
            with transaction.atomic():
                
                user = request.POST.get("user")
                roomId = request.POST.get('roomId')
                
                userForEmail = User.objects.get(pk=user)
                
                user_email = userForEmail.email
                
                
                
                booking = BookRoom.objects.get(user=user, id=roomId)
                room_id = booking.room.id
                room = Room.objects.get(id=room_id)
                
                # Sending mail after room booking is rejected
                send_mail(
                "Room joining request Rejected",
                f"Your request for joining {room.roomTitle} is rejected",
                "room.rent.webapp@gmail.com",
                [user_email],
                fail_silently=False,
                )
                
                
                room.isBooked = False
                bookDate = booking.bookingDate
                bookUser = booking.user
                roomID = booking.room
                canceledBookingDetails = OwnerBookingLog.objects.create(user=bookUser, room=roomID, bookingDate= bookDate, canceledDate= timezone.now(), status='Rejected by Me')
                bookinglog = TenantBookingLog.objects.create(user=bookUser, room=roomID, bookingDate= bookDate, status='Rejected by owner')
                bookinglog.save()
                canceledBookingDetails.save()
                room.save()
                booking.delete() # Reject booking
                sweetify.error(request, "Booking rejected", button='Ok', timer=0)
                step = "canceledBookings"
                return redirect("viewBooking")

        # Initialize an empty list to store pending bookings
        pendingBookings = []
        
        # Iterate over each room and find its pending bookings
        for room in roomsUploadedByUser:
            room_pending_bookings = BookRoom.objects.filter(room=room, joined=False)
            pendingBookings.extend(room_pending_bookings) #extend is used to add elements of an iterable (such as string, list, tuple, set, etc.)
        

        context = {
            'pendingBookings': pendingBookings,
            'step' : step,
            'canceledBookingDetails' : canceledBookingDetails,
            'bookingLog' : bookingLog,
        }
        return render(request, 'Rooms/viewBooking.html', context)
    except:
        sweetify.error(request, 'Something went wrong!',   button='Ok', timer=0)
        return redirect('index')
        

@user_passes_test(is_tenant)
def savedRooms(request):
    try:
        mySavedRooms = SavedRoom.objects.filter(user=request.user)
        # Retrieve the data from the request.POST dictionary
        if 'page' in request.POST:
            pageName = request.POST.get('page')
            return redirect("roomMoreDetails", room_id = pageName)

        context = {
            "mySavedRooms" : mySavedRooms
        }
        return render(request, 'Rooms/savedRooms.html', context)
    except:
        sweetify.error(request, 'Something went wrong!',   button='Ok', timer=0)
        return redirect('index')

@login_required(login_url='signin')
@user_passes_test(is_owner)
def roomIssues(request):
    try:
        allIssues = []
        Allrooms = Room.objects.filter(user=request.user)
        
        for rooms in Allrooms:
            filteredRooms = RoomIssuesOrMaintenance.objects.filter(room=rooms)
            allIssues.extend(filteredRooms)
        
        if request.method == 'POST' and "markIssueAsRead" in request.POST:
            issueID = request.POST.get("issueID")
            RoomIssuesInstance = RoomIssuesOrMaintenance.objects.get(pk=issueID)
            RoomIssuesInstance.status="Updated"
            RoomIssuesInstance.save()
            print("RoomIssuesInstance", RoomIssuesInstance)
            sweetify.success(request, "Issue Marked as Read",button='Ok', timer=0)
            return redirect("roomIssues")
        context = {
            "allIssues" : allIssues
        }
        return render(request, 'Rooms/roomIssues.html', context)
    except:
        sweetify.error(request, 'Something went wrong!',   button='Ok', timer=0)
        return redirect('index')