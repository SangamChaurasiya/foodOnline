from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from vendor.models import Vendor
from menu.models import Category, FoodItem
from marketplace.models import Cart
from django.db.models import Prefetch
from marketplace.context_processors import get_cart_counter, get_cart_amounts
from django.contrib.auth.decorators import login_required
from django.db.models import Q


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }

    return render(request, 'marketplace/listings.html', context)


def vendor_details(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/vendor_details.html', context)


def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        # Checking if request is coming from AJAX or not
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Check if user has already added that food in the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    # Increase the cart quantity
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status': 'Success', 'message': "Increased the cart quantity", 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'Added the food to the cart', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This food does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})

    return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        # Checking if request is coming from AJAX or not
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if the food item exist
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Check if user has already added that food in the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if chkCart.quantity > 1:
                        # Decrease the cart quantity
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity = 0
                    return JsonResponse({'status': 'Success', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'You do not have this item in your cart!'})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This food does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})

    return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)


@login_required(login_url='accounts/login')
def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        # Checking if request is coming from AJAX or not
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # Chaeck if the cart item exists
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': "Success", 'message': "Cart item has been deleted successfully!", 'cart_counter': get_cart_counter(request), 'cart_amount': get_cart_amounts(request)})
            except:
                return JsonResponse({'status': "Failed", 'message': "Cart item does not exist!"})
        else:
            return JsonResponse({'status': "Failed", 'message': "Invalid request!"})
    return render(request, 'delete_cart.html')


def search(request):
    address = request.GET.get("address")
    latitude = request.GET.get("lat")
    longitude = request.GET.get("lng")
    radius = request.GET.get('radius')
    keyword = request.GET.get("keyword")
    
    # get the vendor ids that has the food item the user is looking for
    fetch_vendors_by_food_item = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)
    print(fetch_vendors_by_food_item)

    # Get the vendors either with food name or restaurant name
    vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_food_item) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
    
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }
    return render(request, 'marketplace/listings.html', context)