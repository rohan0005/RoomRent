from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from userManagement.checkUserGroup import *
from room.models import *
from .models import *
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import date, timedelta, datetime
import sweetify
from dateutil.relativedelta import relativedelta
from django.core.mail import send_mail

import requests
import json

def initkhalti(request):
    
    user = request.user.username
    userdetail = request.user
    contact = userdetail.useradditionaldetail.contact_number
    email = userdetail.email

    url = "https://a.khalti.com/api/v2/epayment/initiate/"
    
    return_url = request.POST.get('return_url')
    purchase_order_id = request.POST.get('purchase_order_id')
    amount = request.POST.get('amount')


    payload = json.dumps({
        "return_url": return_url,
        "website_url": "http://127.0.0.1:9900",
        "amount": amount,
        "purchase_order_id": purchase_order_id,
        "purchase_order_name": "test",
        "customer_info": {
        "name": user,
        "email": email,
        "phone": contact,
        }
    })
    headers = {
        'Authorization': 'key c650420ffbdc4da58e4218f4cda0be69', #while deploying this project this secret key should be hidden for that we need to Add SECRET KEY in .env file
        'Content-Type': 'application/json',
    }

    try:
        
        response = requests.request("POST", url, headers=headers, data=payload)
        new_res = json.loads(response.text)

        if new_res['payment_url']:
            return redirect(new_res['payment_url'])
            return redirect("verify")
        
        else:
            sweetify.error(request, "Something went wrong.")
            return redirect("billing")
    except KeyError:
        return redirect("error") 
        

    
def verifyKhalti(request):
    url = "https://a.khalti.com/api/v2/epayment/lookup/"
    if request.method == 'GET':
        headers = {
            'Authorization': 'key c650420ffbdc4da58e4218f4cda0be69',        #2aa019ce6077451bbcf1e39a75cc04c5   #new 5dc172b947fd4aeebfe722a6a0aa3148  #13a1ca52c9fc420295ea401a3b546306
            'Content-Type': 'application/json',
        }
        pidx = request.GET.get('pidx')
        
        payload = json.dumps({
        'pidx': pidx
        })
        
        res = requests.request('POST',url,headers=headers,data=payload)
        
        # return render(request, "Payment/verify.html")
        new_res = json.loads(res.text)
        print("new_res",new_res)
        
        try:
            
            if new_res['status'] == 'Completed':
                
                total_amount = new_res['total_amount']
                transaction_id = new_res['transaction_id']
                
                ini_time_for_now = datetime.now().date()
                currentUser=request.user
                
                booked_room = get_object_or_404(BookRoom, user=request.user, joined=True)
                room_bill = get_object_or_404(RoomBilling, bookedRoom=booked_room)
                
                billedDate = booked_room.rentBilledDate.date()
                print("billedDate:", billedDate)
                
                # CALCULATE THE LATE PAYMENt
                late =  str(ini_time_for_now - \
                             billedDate)
                if "days" in late.split(',')[0].strip() or "day" in late.split(',')[0].strip():
                    lateDay = late.split(',')[0].strip()  # extracting the first part days
                    if "-" in lateDay:
                        late_Days = int(0)
                    else:
                        late_Days = int(lateDay[0].strip())
                else:
                    late_Days = int(0)
                
                nextBillDate = billedDate + relativedelta(months=1)  # Change the next bill date to another month date


                print("new_datenew_datenew_date: ", nextBillDate)
                
                if room_bill.hasChargeLatePaymentFee == True:
                    late_fee = late_Days * 50 # Calculate the late fee if owner has charge late payment
                else:
                    late_fee = 0 
                
                if room_bill.deposit == 0:
                    deposited_amount = booked_room.room.rent
                else:
                    deposited_amount = 0

                try:
                    with transaction.atomic():
                        
                        # CREATE THE OBJECT HERE FOR PaymentHistory Model
                        payment_history = PaymentHistory.objects.create(
                            room=booked_room.room,
                            tenantUser=request.user,
                            paidDate = ini_time_for_now,
                            billedDate = billedDate,
                            lateDays = late_Days,
                            lateFee= late_fee,
                            depositedAmount = deposited_amount,
                            totalPaidAmount = total_amount,
                            transactionID = transaction_id
                        )
                        
                        payment_history.save()
                        
                        # In BookRoom Model assign the rent billed date to next month date
                        booked_room.rentBilledDate = nextBillDate
                        booked_room.save()

                        if room_bill.deposit == 0:  # If deposite is 0  then store the deposite
                            room_bill.deposit = booked_room.room.rent
                            
                        # Update other details of RoomBilling model after payment completed
                        room_bill.status = 'pending'
                        
                        # Update the electricity unit
                        # store the current unit in previous unit and make current unit 0
                        currentUnitForPreviousUnit = room_bill.electricityCurrentUnit
                        room_bill.electricityPreviousUnit = currentUnitForPreviousUnit
                        
                        room_bill.electricityUnit = 0
                        room_bill.electricityAmount = 0
                        room_bill.totalRoomRentAmount= 0
                        room_bill.save()
                        
                        return render(request, "Payment/verify.html")

                except Exception as e:
                    print("An error occurred:", e)
                    return redirect('error')
                
            else:
                return redirect('error')
            
        except KeyError:
            return redirect("error") 
            


    
    
def error(request):
    return render(request, "Payment/error.html")
    




    
# CALCULATE BILLS / late payment fess
@login_required(login_url='signin')
@user_passes_test(is_tenant_or_owner)
def billing(request):
    step = None
    allPendingRoombillings = []
    allUpdatedRentBillings = []
    # For changing same page
    if request.method == 'POST' and 'pendingUpdate' in request.POST:
        step = 'pendingUpdate'
    
    elif request.method == 'POST' and 'updated' in request.POST:
        step = 'updated'
        
    elif request.method == 'POST' and 'paid' in request.POST:
        step = 'paid'
    
    
    #FOR TENANT
    bookedRoomByCurrentUser = BookRoom.objects.filter(user=request.user, joined= True).first()
    rentBillForCurrentUser = RoomBilling.objects.filter(bookedRoom=bookedRoomByCurrentUser, status="updated")
    
    # FOR owner
    today = date.today() #gat the today date
    rooms = Room.objects.filter(user=request.user) #Get all the room for current user
    
    for room in rooms: # Getting all the bookedRoom of the current user
        updated_booked_rooms = BookRoom.objects.filter(room=room, joined=True).first()
        UpdatedRentBillings = RoomBilling.objects.filter(bookedRoom=updated_booked_rooms).first()
        if UpdatedRentBillings:
            if UpdatedRentBillings.status == "updated":
                allUpdatedRentBillings.append(UpdatedRentBillings)
                                                            
        booked_rooms = BookRoom.objects.filter(moveInDate__lt=today, room=room, joined=True).first()  # Filter rooms where move-in date is before today OR LESS THAN TODAY
        
        if booked_rooms:
            currentTime = datetime.now().date()
            future_date_after_3days = booked_rooms.rentBilledDate + timedelta(days=3)
            future_date_after_2days = booked_rooms.rentBilledDate + timedelta(days=2)
            future_date_after_1days = booked_rooms.rentBilledDate + timedelta(days=1)
            if future_date_after_3days.date() == booked_rooms.rentBilledDate.date() or future_date_after_2days.date() == booked_rooms.rentBilledDate.date() or future_date_after_1days.date() == booked_rooms.rentBilledDate.date() or currentTime > booked_rooms.rentBilledDate.date() :
                roombilling = RoomBilling.objects.filter(bookedRoom=booked_rooms, status="pending").exclude(id=None).first() #get the instance of RoomBilling
                if roombilling is not None:
                    allPendingRoombillings.append(roombilling)
            
            roombilling = RoomBilling.objects.filter(bookedRoom=booked_rooms, status="pending").exclude(id=None).first() #get the instance of RoomBilling
            if roombilling and booked_rooms.moveInDate == booked_rooms.rentBilledDate:
                move_in_date = booked_rooms.rentBilledDate
                try:
                    next_month_date = move_in_date.replace(month=move_in_date.month + 1)
                    booked_rooms.rentBilledDate = next_month_date
                    booked_rooms.save()
                except ValueError:
                    next_month_date = move_in_date.replace(year=move_in_date.year + 1, month = 1)  #change the year if month is january
                    booked_rooms.rentBilledDate = next_month_date
                    booked_rooms.save()
                    
    if request.method == 'POST' and 'updatePendingRoom' in request.POST:
        roombillingID = request.POST.get('roomBillingID')  
        if "hasLatePaymentCharge" in request.POST:
            # If checked set latePaymentCharge to True
            latePaymentCharge = True
        else:
            # If not checked set latePaymentCharge to False
            latePaymentCharge = False
        updateBilling = RoomBilling.objects.get(pk=roombillingID)
        roomName = updateBilling.bookedRoom.room.roomTitle
        
        userID = updateBilling.bookedRoom.user.id
        
        #send mail
        userForEmail = User.objects.get(pk=userID)
        user_email = userForEmail.email
        
        # Sending mail after room booking is rejected
        send_mail(
        "Room rent bill updated",
        f"Your bill for {roomName} has been generated. Please view and pay it via our website.",
        "room.rent.webapp@gmail.com",
        [user_email],
        fail_silently=False,
        )

        
        rentAmount = request.POST.get('rentAmount')
        print("rentAmount:", rentAmount)
        # UPDAING THE TENANT BILL
            
        with transaction.atomic():
            updateBilling.electricityUnit = request.POST.get('electricityUnit')
            updateBilling.electricityAmount = request.POST.get('electricityAmount')
            updateBilling.totalRoomRentAmount = request.POST.get('totalAmount')
            updateBilling.electricityPreviousUnit = request.POST.get('ElecPreviousUnit')
            updateBilling.electricityCurrentUnit = request.POST.get('ElecCurrentUnit')
            updateBilling.status = "updated"
            updateBilling.hasChargeLatePaymentFee = latePaymentCharge
            updateBilling.save()
            sweetify.success(request, "Bill Updated !!")
        return redirect('billing')
  
          
    print("allPendingRoombillings", allPendingRoombillings)
    context = {
        'step' : step,
        'allPendingRoombillings' : allPendingRoombillings,
        'allUpdatedRentBillings' : allUpdatedRentBillings,
        'rentBillForCurrentUser' : rentBillForCurrentUser,
    }
    
    return render(request, "Payment/rentBill.html", context)

def paymentHistory(request):
    allOwnerPaymentHistory = []
    roomUploadedByOwner = Room.objects.filter(user=request.user)
    if roomUploadedByOwner: #If the owner has room
        for room in roomUploadedByOwner:
            payment_history = PaymentHistory.objects.filter(room=room, hasReleasedFund=True)  # get the payment history for a particular room
            if payment_history is not None:
                for payment in payment_history:
                    allOwnerPaymentHistory.append(payment) # append it to the list allOwnerPaymentHistory
                
                
    roomPaymentFromTenant =  PaymentHistory.objects.filter(tenantUser=request.user) # get the payment history of the current tenant user
    
    print("allOwnerPaymentHistory :", allOwnerPaymentHistory)
    print("roomPaymentFromTenant", roomPaymentFromTenant)
    context = {
        "allOwnerPaymentHistory" : allOwnerPaymentHistory,
        "roomPaymentFromTenant" : roomPaymentFromTenant,
    }
    
    return render(request, "Payment/paymentHistory.html", context)

def paymentHistoryAdminView(request):
    step = None
    if request.method == "POST":
        if "pendingRefunds" in request.POST:
            step = "pendingRefunds"
        elif "completedRefunds" in request.POST:
            step = "completedRefunds"
        elif "refund" in request.POST:
            commissionRate = 0.005    #Commission rate is 0.5%
            paymentHistoryID = request.POST.get("paymentHistoryID")
            print("paymentHistoryID", paymentHistoryID)
            paymentHistory = PaymentHistory.objects.get(pk=paymentHistoryID)
            
            user_email = paymentHistory.room.user.email
            send_mail(
                "Payment Released",
                "Dear Owner,\n\nWe are pleased to inform you that the payment for your room has been successfully released.\n\nThank you for using our platform. \n\nBest regards,\n[RoomRent] Team",
                "room.rent.webapp@gmail.com",
                [user_email],
                fail_silently=False
            )
                        
            # CALCULATION FOR COMMISSION AMOUNT
            amount = paymentHistory.totalPaidAmount
            commissionAmount = amount * commissionRate
            updateTotalAmount = amount - commissionAmount
            
            paymentHistory.hasReleasedFund=True
            paymentHistory.systemCommissionAmount = commissionAmount
            paymentHistory.totalPaidAmount = updateTotalAmount
            paymentHistory.save()  # save the commission and update the total amount
            
            
            
            sweetify.success(request, "Amount Refunded to owner.")

    print("stepppppp:", step)
    allPaymentHistory = PaymentHistory.objects.filter(hasReleasedFund=False)
    allPaymentHistoryWithReleasedFund = PaymentHistory.objects.filter(hasReleasedFund=True)
    context = {
        'allPaymentHistory' : allPaymentHistory,
        "step" : step,
        "allPaymentHistoryWithReleasedFund" : allPaymentHistoryWithReleasedFund,
    }
    return render(request, "Admin/paymentHistoryAdmin.html", context)

