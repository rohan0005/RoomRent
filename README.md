# RoomRent
 A platform which aims to simplify renting process.



## Features
- **User Registration:** Users can register as property owners or tenants by providing necessary details.
- **Room Listing:** Property owners can list their rooms for rent, specifying details such as location, amenities, and rental terms.
- **Room Search:** Tenants can search for available rooms based on their preferences, such as location, price range, and room specifications.
- **Booking Requests:** Tenants can request to book a room, and owners can approve or reject these requests.
- **Billing Management:** The platform provides an integrated billing system for tracking payments, managing rent dues, and calculating utility bills.
- **Feedback and Reviews:** Tenants can submit feedback and reviews after their stay, helping to improve the rental experience.



## Installation

To run the RoomRent platform locally, follow these steps:

1. Install Python
Install python-10 or 11 and python-pip. Follow the steps from the below reference document based on your Operating System. Reference: https://www.tomshardware.com/how-to/install-python-on-windows-10-and-11

2.  Setup virtual environment

    Install Virtual environment
    py -m venv .venv

    Activate the venv
   
        Windows: .\venv\Scripts\activate
        Mac/Linux: source .venv/bin/activate

3.  Clone git repository

        git clone "https://github.com/rohan0005/RoomRent.git"

4.  Install requirements

        cd roomrent/
        pip install -r requirements.txt


6.  Run the migration command

      #### Make migrations
        -python manage.py makemigrations
        -python manage.py migrate

8.  Run the server

    Run the server
    
        python manage.py runserver 8000
      
   # your server is up on port 8000
   # Run this url
       http://127.0.0.1:8000/home

