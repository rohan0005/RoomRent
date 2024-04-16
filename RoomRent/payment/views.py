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
    try:
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
            "website_url": "http://127.0.0.1:9090",
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
                sweetify.error(request, "Something went wrong.",  button='Ok', timer=0)
                return redirect("billing")
        except KeyError:
            return redirect("error")
    except:
        sweetify.error(request, 'Something went wrong.',   button='Ok', timer=0)
        return redirect('index')

    
def verifyKhalti(request):
    try:
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
                                transactionID = transaction_id,
                                electricityPreviousUnit = room_bill.electricityPreviousUnit,
                                electricityCurrentUnit = room_bill.electricityCurrentUnit,
                                wasChargedLateFee = room_bill.hasChargeLatePaymentFee,
                                electricityUnit = room_bill.electricityUnit,
                                electricityAmount = room_bill.electricityAmount,
                                waterCharge = booked_room.room.water,
                                TrashCharge = booked_room.room.trash,
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
                            sweetify.success(request, "Payment completed successfully", button='Ok', timer=0)
                            return redirect('billing')

                    except Exception as e:
                        print("An error occurred:", e)
                        sweetify.error(request, "Something went wrong during your payment.", button='Ok', timer=0)
                        return redirect('billing')
                    
                else:
                    sweetify.error(request, "Something went wrong during your payment.", button='Ok', timer=0)
                    return redirect('billing')
                
            except KeyError:
                sweetify.error(request, "Something went wrong during your payment.", button='Ok', timer=0)
                return redirect('billing')
    except:
        sweetify.error(request, 'Something went wrong.',   button='Ok', timer=0)
        return redirect('index')   

    
# CALCULATE BILLS / late payment fess
@login_required(login_url='signin')
@user_passes_test(is_tenant_or_owner)
def billing(request):
    try:
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
        today = date.today() #get the today date
        print("today", today)
        rooms = Room.objects.filter(user=request.user) #Get all the room for current user
        
        for room in rooms: # Getting all the bookedRoom of the current user
            updated_booked_rooms = BookRoom.objects.filter(room=room, joined=True).first()
            UpdatedRentBillings = RoomBilling.objects.filter(bookedRoom=updated_booked_rooms).first()
            if UpdatedRentBillings:
                if UpdatedRentBillings.status == "updated":
                    allUpdatedRentBillings.append(UpdatedRentBillings)
                                                    
            booked_rooms = BookRoom.objects.filter(moveInDate__lt = today, room=room, joined=True).first()
            print("yoo", booked_rooms)
            # Filter rooms where move-in date is before today OR LESS THAN TODAY
            print("booked_roomsLT", booked_rooms)
            if booked_rooms:
                currentTime = datetime.now().date()
                print("currentTime", currentTime)
                date_before_3days = (booked_rooms.rentBilledDate - timedelta(days=3)).date()
                date_before_2days = (booked_rooms.rentBilledDate - timedelta(days=2)).date()
                date_before_1days = (booked_rooms.rentBilledDate - timedelta(days=1)).date()
                date_with_changed_time_before_1days = date_before_1days + timedelta(days=1)
                print("date_before_3days", date_before_3days)
                print("date_before_2days", date_before_2days)
                print("date_before_1days", date_before_1days)
                
                print("date_and_before_1days", date_with_changed_time_before_1days)
                print("booked_rooms.rentBilledDate ", booked_rooms.rentBilledDate.date())
                if date_before_3days == booked_rooms.rentBilledDate.date() or date_before_2days == booked_rooms.rentBilledDate.date() or date_before_1days == booked_rooms.rentBilledDate.date() or currentTime >= booked_rooms.rentBilledDate.date() or date_with_changed_time_before_1days == booked_rooms.rentBilledDate.date():
                    print("date_before_3days", date_before_3days)
                    print("date_before_2days", date_before_2days)
                    print("date_before_1days", date_before_1days)
                    roombilling = RoomBilling.objects.filter(bookedRoom=booked_rooms, status="pending").exclude(id=None).first() #get the instance of RoomBilling
                    print("roombilling", roombilling)
                    if roombilling is not None:
                        allPendingRoombillings.append(roombilling)

                        
        if request.method == 'POST' and 'updatePendingRoom' in request.POST:
            ElecPreviousUnit = request.POST.get('ElecPreviousUnit')
            ElecCurrentUnit = request.POST.get('ElecCurrentUnit')
            if ElecPreviousUnit >= ElecCurrentUnit:
                sweetify.error(request, 'Current Unit cannot be less than or equal to Previous Unit.', button='Ok', timer=0)
                return redirect('billing')
                
            
            
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
                sweetify.success(request, "Bill Updated !!", button='Ok', timer=0)
            return redirect('billing')
    
            
        print("allPendingRoombillings", allPendingRoombillings)
        context = {
            'step' : step,
            'allPendingRoombillings' : allPendingRoombillings,
            'allUpdatedRentBillings' : allUpdatedRentBillings,
            'rentBillForCurrentUser' : rentBillForCurrentUser,
        }
        
        return render(request, "Payment/rentBill.html", context)
    except:
        sweetify.error(request, 'Something went wrong.',   button='Ok', timer=0)
        return redirect('index')
    
@login_required(login_url='signin')
@user_passes_test(is_tenant_or_owner)
def paymentHistory(request):
    try:
        
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

    except:
        sweetify.error(request, 'Something went wrong.',   button='Ok', timer=0)
        return redirect('index')

@user_passes_test(is_superuser)
def paymentHistoryAdminView(request):
    try:
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
                
                
                
                sweetify.success(request, "Amount Refunded to owner.",  button='Ok', timer=0)

        print("stepppppp:", step)
        allPaymentHistory = PaymentHistory.objects.filter(hasReleasedFund=False)
        allPaymentHistoryWithReleasedFund = PaymentHistory.objects.filter(hasReleasedFund=True)
        context = {
            'allPaymentHistory' : allPaymentHistory,
            "step" : step,
            "allPaymentHistoryWithReleasedFund" : allPaymentHistoryWithReleasedFund,
        }
        return render(request, "Admin/paymentHistoryAdmin.html", context)
    except:
        sweetify.error(request, 'Something went wrong.',   button='Ok', timer=0)
        return redirect('index')        
