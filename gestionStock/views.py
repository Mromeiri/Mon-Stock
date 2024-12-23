from django.contrib.auth import logout
from django.shortcuts import redirect
from django.shortcuts import render
from admin_soft.forms import RegistrationForm, LoginForm, UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm
from django.contrib.auth.models import User

def admin_logout(request):
    logout(request)
    # Redirect to the admin login page or another suitable location
    return redirect('/admin/login/?next=/admin/')
def index(request):
    # Your view logic here
    return render(request, 'index.html')

# class TopFournisseur(View):
#     def get(self, request , *args **)
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Check if a user with the provided email already exists
            if User.objects.filter(email=email).exists():
                form.add_error('email', 'This email is already in use. Please choose another one.')
            else:
                # Create a new user only if the email is not already registered
                form.save()
                print('Account created successfully!')
                return redirect('/admin/login/?next=/admin/')
        else:
            print("Registration failed!")
    else:
        form = RegistrationForm()

    context = {'form': form}
    return render(request, 'accounts/register.html', context)