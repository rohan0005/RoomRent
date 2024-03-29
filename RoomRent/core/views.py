from django.shortcuts import render
import sweetify

# Create your views here.
def index(request):
    return render(request, 'Landing page/index.html')

def checkValidity(request):
    sweetify.error(request, 'You are not authorized to view this page.', timer= 8000)
    return render(request, 'Landing page/index.html')