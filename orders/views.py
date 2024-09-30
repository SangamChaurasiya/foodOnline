from django.shortcuts import render, redirect
from marketplace.models import Cart, Tax
from marketplace.context_processors import get_cart_amounts
from orders.forms import OrderForm
from orders.models import Order, Payment, OrderedFood
from menu.models import FoodItem
from orders.utils import generate_order_number
from django.http import JsonResponse, HttpResponse
import simplejson as json
from accounts.utils import sendNotification
from django.contrib.auth.decorators import login_required
from foodOnline_main.settings import RZP_KEY_ID, RZP_KEY_SECRET
import razorpay


client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))


@login_required(login_url="accounts:login")
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace:marketplace')

    vendors_ids = []
    for i in cart_items:
        if i.fooditem.vendor.id not in vendors_ids:
            vendors_ids.append(i.fooditem.vendor.id)

    # {"vendor_id": {"subtotal": {"tax_type": {"tax_percentage": "tax_amount"}}}}
    subtotal = 0
    k = {}
    get_tax = Tax.objects.filter(is_active=True)
    total_data = {}
    for i in cart_items:
        fooditem = FoodItem.objects.get(pk=i.fooditem.id, vendor_id__in=vendors_ids)
        v_id = fooditem.vendor.id
        if v_id in k:
            subtotal = k[v_id]
            subtotal += (fooditem.price * i.quantity)
        else:
            subtotal = (fooditem.price * i.quantity)
        k[v_id] = subtotal

        # Calculate the tax data
        
        tax_dict = {}
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage * subtotal)/100, 2)
            tax_dict.update({tax_type: {str(tax_percentage): str(tax_amount)}})

        # Construct total data
        total_data.update({fooditem.vendor.id: {str(subtotal): str(tax_dict)}})
    subtotal = get_cart_amounts(request)['subtotal']
    total_tax = get_cart_amounts(request)['tax']
    grand_total = get_cart_amounts(request)['grand_total']
    tax_data = get_cart_amounts(request)['tax_dict']

    if request.method == "POST":
        form = OrderForm(request.POST)

        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data.get('first_name')
            order.last_name = form.cleaned_data.get('last_name')
            order.phone = form.cleaned_data.get('phone')
            order.email = form.cleaned_data.get('email')
            order.address = form.cleaned_data.get('address')
            order.country = form.cleaned_data.get('country')
            order.state = form.cleaned_data.get('state')
            order.city = form.cleaned_data.get('city')
            order.pin_code = form.cleaned_data.get('pin_code')
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_data = json.dumps(total_data)
            order.total_tax = total_tax
            order.payment_method = request.POST.get('payment_method')
            order.save() # order id/pk is generated
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendors_ids)
            order.save()

            if order.payment_method == "RazorPay":
                # RazorPay Payment
                DATA = { 
                    "amount": float(order.total) * 100, 
                    "currency": "INR", 
                    "receipt": "receipt #" + order.order_number,
                    "notes": {
                        "key1": "value3",
                        "key2": "value2",
                    }
                }

                # creating RazorPay order
                rzp_order = client.order.create(data=DATA)
                rzp_order_id = rzp_order['id']

            context = {
                'order': order,
                'cart_items': cart_items,
                # 'rzp_order_id': rzp_order_id,
                # 'rzp_amount': float(order.total) * 100,
                # 'RZP_KEY_ID': RZP_KEY_ID,
            }
            return render(request, 'orders/place_order.html', context)
        else:
            print(form.errors)
    return render(request, 'orders/place_order.html')


@login_required(login_url="accounts:login")
def payments(request):
    # Check if request is ajax or not
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        # STORE THE PAYMENT DETAILS IN THE PAYMENT MODEL
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')

        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user=request.user,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=order.total,
            status=status
        )
        payment.save()

        # UPDATE THE ORDER MODEL
        order.payment = payment
        order.is_ordered = True
        order.save()

        # MOVE THE CART ITEMS TO ORDERED FOOD MODEL
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood()
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.fooditem = item.fooditem
            ordered_food.quantity = item.quantity
            ordered_food.price = item.fooditem.price
            ordered_food.amount = item.fooditem.price * item.quantity # total amount
            ordered_food.save()

        # SEND ORDER CONFORMATION EMAIL TO THE CUSTOMER
        mail_subject = "Thank you for ordering with us."
        mail_template = "orders/order_confirmation_email.html"
        context = {
            'user': request.user,
            'order': order,
            'to_email': order.email,
        }

        sendNotification(mail_subject, mail_template, context)

        # SEND ORDER RECEIVED EMAIL TO THE VENDOR
        mail_subject = "You have received a new order."
        mail_template = "orders/new_order_received.html"
        to_emails = []
        for i in cart_items:
            if i.fooditem.vendor.user.email not in to_emails:
                to_emails.append(i.fooditem.vendor.user.email)

        context = {
            'order': order,
            'to_email': to_emails,
        }
        sendNotification(mail_subject, mail_template, context)

        # CLEAR THE CART IF THE PAYMENT IS SUCCESS
        cart_items.delete()

        # RETURN BACK TO AJAX WITH THE STATUS SUCCESS OR FAILURE
        response = {
            'order_number': order_number,
            'transaction_id': transaction_id,
        }
        return JsonResponse(response)
    return HttpResponse("Payment View")


def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)

        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)
        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }
        return render(request, 'orders/order_complete.html', context=context)
    except:
        return redirect('home')
