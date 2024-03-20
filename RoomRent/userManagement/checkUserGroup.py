# Check if user is tenant or not
def is_tenant(user):
    return user.groups.filter(name='tenant').exists()


def is_owner(user):
    return user.groups.filter(name='owner').exists()

# Check if user is tenant or owner
def is_tenant_or_owner(user):
    return user.is_authenticated and user.groups.filter(name='tenant').exists() or user.groups.filter(name='owner').exists()
