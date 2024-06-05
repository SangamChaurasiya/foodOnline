from django.shortcuts import render, redirect
from accounts.forms import UserForm
from accounts.models import User
from django.contrib import messages, auth
from accounts.utils import detectUser
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied


# Restricting the Customer from accessing the Vendor page
def checkRoleCustomer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect('accounts:myAccount')
    elif request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            # # Creating the user using the form
            # password = form.cleaned_data.get('password')
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()

            # Creating the user using the create_user() method
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            username = form.cleaned_data.get('username')
            email= form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, "Your account has been registered successfully!")

            return redirect('accounts:registerUser')
        else:
            pass
    else:
        form = UserForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/registerUser.html', context)


def login(request):
    if request.user.is_authenticated:
        return redirect('accounts:myAccount')
    elif request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect('accounts:myAccount')
        else:
            messages.error(request, "Invalid Login Credentials!")
            return redirect('accounts:login')
    return render(request, 'accounts/login.html')


def logout(request):
    auth.logout(request)
    messages.info(request, "You are logged out.")
    return redirect('accounts:login')


@login_required(login_url='accounts:login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)


@login_required(login_url='accounts:login')
@user_passes_test(checkRoleCustomer)
def customerDashboard(request):
    print(request.user.get_role())
    return render(request, 'accounts/customerDashboard.html')
