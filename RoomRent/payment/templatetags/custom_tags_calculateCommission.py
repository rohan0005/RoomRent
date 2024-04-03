# TO CALCULATE COMMISSION AMOUNT CREATING A CUSTOM FILTER AND REGISTERING IT.
from django import template

register = template.Library()

@register.filter
def calculateCommission(total_paid_amount):
    return total_paid_amount * 0.005             #Commission rate is 0.5 %