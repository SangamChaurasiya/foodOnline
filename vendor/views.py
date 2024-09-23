from django.shortcuts import render, redirect, get_object_or_404
from accounts.forms import UserForm, UserProfileForm
from vendor.forms import VendorForm
from accounts.models import User, UserProfile
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from accounts.utils import sendEmail
from vendor.models import Vendor


# Restricting the Vendor from accessing the Customer page
def checkRoleVendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied
    

def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect('accounts:myAccount')
    elif request.method == "POST":
        # Store the data and create the user
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)

        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            username = form.cleaned_data.get('username')
            email= form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.VENDOR
            user.save()

            vendor = v_form.save(commit=False)
            vendor.user = user

            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            
            vendor.save()

            # # Send Verification Email
            mailSubject = "Please activate your account"
            emailTemplate = "accounts/emails/accountVerificationEmail.html"
            sendEmail(request, user, mailSubject, emailTemplate)

            messages.success(request, "Your account has been registered successfully!, please wait for the approval.")

            return redirect('vendor:registerVendor')
        else:
            print("Invalid Form")
            print(form.errors)
            print(v_form.errors)
    else:
        form = UserForm()
        v_form = VendorForm()

    context = {
        'form': form,
        'v_form': v_form
    }

    return render(request, 'vendors/registerVendor.html', context)


@login_required(login_url="accounts:login")
@user_passes_test(checkRoleVendor)
def vendorDashboard(request):
    return render(request, 'vendors/vendorDashboard.html')


@login_required(login_url='accounts:login')
@user_passes_test(checkRoleVendor)
def vprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)

        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, "Settings Updated.")
            return redirect("vendor:vprofile")
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor
    }
    return render(request, 'vendors/vprofile.html', context)
