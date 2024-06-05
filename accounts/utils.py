def detectUser(user):
    if user.role == 1:
        return "vendor:vendorDashboard"
    elif user.role == 2:
        return "accounts:customerDashboard"
    elif user.role == None and user.is_superadmin:
        return "/admin"