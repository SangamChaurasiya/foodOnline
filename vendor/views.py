from django.shortcuts import render, redirect
from accounts.forms import UserForm
from vendor.forms import VendorForm
from accounts.models import User, UserProfile
from vendor.models import Vendor
from django.contrib import messages


# Create your views here.
def registerVendor(request):
    # Store the data and create the user
    if request.method == "POST":
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

            messages.success(request, "Vendor has been registered successfully!, please wait for the approval.")

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
