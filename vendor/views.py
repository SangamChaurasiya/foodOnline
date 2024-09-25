from django.shortcuts import render, redirect, get_object_or_404
from accounts.forms import UserForm, UserProfileForm
from vendor.forms import VendorForm
from accounts.models import User, UserProfile
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from accounts.utils import sendEmail
from vendor.models import Vendor
from menu.models import Category, FoodItem
from menu.forms import CategoryForm, FoodItemForm
from django.template.defaultfilters import slugify


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
            vendor_name = v_form.cleaned_data['vendor_name']
            vendor.vendor_slug = slugify(vendor_name) + '-' + str(user.id)

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

    return render(request, 'vendor/registerVendor.html', context)


@login_required(login_url="accounts:login")
@user_passes_test(checkRoleVendor)
def vendorDashboard(request):
    return render(request, 'vendor/vendorDashboard.html')


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
    return render(request, 'vendor/vprofile.html', context)


def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor


@login_required(login_url="accounts:login")
@user_passes_test(checkRoleVendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by("created_at")
    context = {
        'categories': categories
    }
    return render(request, 'vendor/menu_builder.html', context=context)


@login_required(login_url="accounts:login")
@user_passes_test(checkRoleVendor)
def fooditems_by_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
    context = {
        'fooditems': fooditems,
        'category': category
    }
    return render(request, 'vendor/fooditems_by_category.html', context)


@login_required(login_url="accounts:login")
@user_passes_test(checkRoleVendor)
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, "Category added successfully!")
            return redirect('vendor:menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    context = {
        'form': form
    }
    return render(request, 'vendor/add_category.html', context)


@login_required(login_url="accounts:login")
@user_passes_test(checkRoleVendor)
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect('vendor:menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm(instance=category)
    context = {
        'form': form,
        'category': category
    }
    return render(request, 'vendor/edit_category.html', context)


@login_required(login_url="accounts:login")
@user_passes_test(checkRoleVendor)
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category has been deleted successfully.")
    return redirect('vendor:menu_builder')


@login_required(login_url="accounts:login")
@user_passes_test(checkRoleVendor)
def add_food(request):
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(food_title)
            form.save()
            messages.success(request, "Food added successfully!")
            return redirect('vendor:fooditems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm()

        # modify the form
        form.fields["category"].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form
    }
    return render(request, 'vendor/add_food.html', context)


@login_required(login_url="accounts:login")
@user_passes_test(checkRoleVendor)
def edit_food(request, pk):
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(food_title)
            form.save()
            messages.success(request, "Food item updated successfully!")
            return redirect('vendor:fooditems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm(instance=food)
        # modify the form
        form.fields["category"].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
        'food': food
    }
    return render(request, 'vendor/edit_food.html', context)


@login_required(login_url="accounts:login")
@user_passes_test(checkRoleVendor)
def delete_food(request, pk):
    food = get_object_or_404(FoodItem, pk=pk)
    category_id = food.category.id
    food.delete()
    messages.success(request, "Food item has been deleted successfully.")
    return redirect('vendor:fooditems_by_category', category_id)
