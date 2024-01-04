from django.contrib.auth import logout
from django.shortcuts import redirect

def admin_logout(request):
    logout(request)
    # Redirect to the admin login page or another suitable location
    return redirect('/admin/login/?next=/admin/')
