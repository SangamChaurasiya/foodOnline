from django.shortcuts import render, redirect
from accounts.forms import UserForm
from accounts.models import User
from django.contrib import messages, auth
from accounts.utils import detectUser, send_verification_email
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from orders.models import Order


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

            # Send Verification Email
            mailSubject = "Please activate your account"
            emailTemplate = "accounts/emails/accountVerificationEmail.html"
            send_verification_email(request, user, mailSubject, emailTemplate)

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


def activate(request, uidb64, token):
    # Activate the user by setting the is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! you account is activated.")
    else:
        messages.error(request, "Invalid activation link.")
    return redirect('accounts:myAccount')


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
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    recent_orders = orders[:5]

    context = {
        'orders': orders,
        'recent_orders': recent_orders,
        'orders_count': orders.count()
    }
    return render(request, 'accounts/customerDashboard.html', context)


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # Send Reset Password Email
            mailSubject = "Reset Your Password"
            emailTemplate = "accounts/emails/resetPasswordEmail.html"
            send_verification_email(request, user, mailSubject, emailTemplate)
            messages.success(request, "Reset Password link has been sent to your email address.")
            return redirect('accounts:login')
        else:
            messages.error(request, "Account does not exist.")
            return redirect('accounts:forgotPassword')
    return render(request, 'accounts/forgotPassword.html')


def resetPasswordValidate(request, uidb64, token):
    uid = ''
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.info(request, "Please reset your password.")
        return redirect('accounts:resetPassword')
    else:
        messages.error(request, "This link has been expired.")
        return redirect('accounts:myAccount')


def resetPassword(request):
    if request.method == "POST":
        nPassword = request.POST.get("nPassword")
        cPassword = request.POST.get("cPassword")
        if nPassword != cPassword:
            messages.error(request, "Passwords do not match.")
            return redirect('accounts:resetPassword')
        else:
            uid = request.session.get('uid')
            user = User.objects.get(pk=uid)
            user.set_password(nPassword)
            user.is_active = True
            user.save()
            messages.success(request, "Your password has been changed successfully.")
            return redirect('accounts:login')
    return render(request, 'accounts/resetPassword.html')

