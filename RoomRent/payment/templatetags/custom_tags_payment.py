from django import template
from django.contrib.auth.models import Group 

register = template.Library() 

@register.filter(name='has_group') 
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()




@register.filter
def extract_days_since(value):
    try:
        if "days" in value.split(',')[0].strip() or "day" in value.split(',')[0].strip():
            days_since = value.split(',')[0].strip()  # extracting the first part days
            return days_since[0]  # get the days only
        else:
            return "0"
    except AttributeError:
        return value  # returning the original value if there is some error
    
@register.filter
def multiply(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return value