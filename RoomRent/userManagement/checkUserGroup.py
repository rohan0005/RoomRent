# Check if user is tenant or not
def is_tenant(user):
    if user.useradditionaldetail.has_blocked == True:
        return user.is_authenticated and user.useradditionaldetail.has_blocked == False and user.groups.filter(name='tenant').exists() 
    elif user.is_authenticated and user.useradditionaldetail.has_blocked == False and user.groups.filter(name='tenant').exists():
        return user.is_authenticated and user.useradditionaldetail.has_blocked == False and user.groups.filter(name='tenant').exists() 

def is_owner(user):
    if user.useradditionaldetail.has_blocked == True:
        return user.is_authenticated and user.useradditionaldetail.has_blocked == False and user.groups.filter(name='owner').exists() 
    elif user.is_authenticated and user.useradditionaldetail.has_blocked == False and user.groups.filter(name='owner').exists():
        return user.is_authenticated and user.useradditionaldetail.has_blocked == False and user.groups.filter(name='owner').exists() 


# return superuser
def is_superuser(user):
    return user.is_superuser


# Check if user is tenant or owner
def is_tenant_or_owner(user):
    if user.useradditionaldetail.has_blocked == True:
        return user.is_authenticated and user.useradditionaldetail.has_blocked == False and (user.groups.filter(name='tenant').exists() or user.groups.filter(name='owner').exists()) 
    elif user.is_authenticated and user.useradditionaldetail.has_blocked == False and (user.groups.filter(name='tenant').exists() or user.groups.filter(name='owner').exists()):
        return user.is_authenticated and user.useradditionaldetail.has_blocked == False and (user.groups.filter(name='tenant').exists() or user.groups.filter(name='owner').exists()) 
