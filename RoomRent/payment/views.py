from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from userManagement.checkUserGroup import *
from room.models import *
from .models import *
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import date, timedelta


import requests
import json

@login_required(login_url='signin')
@user_passes_test(is_tenant)
def myBalance(request):
    hasBooking = BookRoom.objects.filter(user=request.user).first()  # there is only one object so we used .first()
    balance = MyBalance.objects.filter(bookedRoom=hasBooking)
    
    context = {
        'hasBooking' : hasBooking,
        'balance' : balance,
    }
    
    return render(request, 'Payment/myBalance.html', context)

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
        "website_url": "http://127.0.0.1:8000",
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
            return redirect("mybalance")
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
        

        if new_res['status'] == 'Completed':
            booked_room = get_object_or_404(BookRoom, user=request.user)
            amount = new_res['total_amount']
            balance = MyBalance.objects.get(bookedRoom=booked_room)

            balance.amount += amount
            balance.amountUpdatedOn = timezone.now()
            balance.save()

            return render(request, "Payment/verify.html")
        
        else:
            return redirect('error')


    
    
def error(request):
    return render(request, "Payment/error.html")
    




    
# CALCULATE BILLS / late payment fess
@login_required(login_url='signin')
@user_passes_test(is_tenant_or_owner)
def billing(request):
    bookedRoomByCurrentUser = BookRoom.objects.filter(user=request.user, joined= True).first()
    rentBill = RoomBilling.objects.filter(bookedRoom=bookedRoomByCurrentUser)
    print("REBTTTTTTTTT: ", bookedRoomByCurrentUser)
    print("REBTTTTTTTTT: ", rentBill)
    
    today = date.today()
    booked_rooms = BookRoom.objects.filter(moveInDate__lt=today)  # Filter rooms where move-in date is before today OR LESS THAN TODAY
    
    roomBilling = [] 
    collectRentForThisRoom = []
       
    for room in booked_rooms:
        Billing = RoomBilling.objects.filter(bookedRoom=room).first()
        roomBilling.append(Billing)
        
    for room in booked_rooms:
        move_in_date = room.moveInDate
        if move_in_date.month != today.month or (move_in_date.month == today.month and move_in_date.year != today.year ):  # Check if move-in date month is different from today's month and YEAR NE CHECK
            
            # check if billing date is after 3 days or not
            if today.day  + 1 == move_in_date.day or today.day  + 2 == move_in_date.day or today.day  + 3 == move_in_date.day or today.day == move_in_date.day:
                
                collectRentForThisRoom.append(room)
                
                # Get the day of the move-in date
                move_in_day = move_in_date.day
                
                # Update move-in date to the same day next month
                next_month_date = move_in_date.replace(month=move_in_date.month + 1)
                # If move-in month was December, adjust year as well
                if next_month_date.month == 1:
                    next_month_date = next_month_date.replace(year=move_in_date.year + 1)
                
                # Store the next next billing date
                room.rentBilledDate = next_month_date
                room.save()

          
    print("collectRentForThisRoom", collectRentForThisRoom)
    
    if request.method == 'POST' :
        electricityUnit = request.POST.get('electricityUnit')
        electricityAmount = request.POST.get('electricityAmount')
        totalAmount = request.POST.get('totalAmount')
        
        for room in booked_rooms:
            with transaction.atomic():
                billing = RoomBilling.objects.create(bookedRoom=room, electricityUnit = electricityUnit, electricityAmount = electricityAmount, totalRoomRentAmount = totalAmount)
                billing.save()
                
                electricityDetail = ElectricityUnitDetail.objects.filter(bookedRoom=room)
                for detail in electricityDetail:
                    detail.status = 'Updated'
                    detail.save()
              
    context = {
            'collectRentForThisRoom' : collectRentForThisRoom,
            'roomBilling' : roomBilling,
            'rentBill' : rentBill,
        }
    
    return render(request, "Payment/rentBill.html", context)

