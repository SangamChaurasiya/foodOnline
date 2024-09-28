from django.shortcuts import render, redirect
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amounts
from orders.forms import OrderForm
from orders.models import Order
from orders.utils import generate_order_number
import simplejson as json


def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace:marketplace')
    
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
            order.total_tax = total_tax
            order.payment_method = request.POST.get('payment_method')
            order.save() # order id/pk is generated
            order.order_number = generate_order_number(order.id)
            order.save()
            return redirect('orders:place_order')
        else:
            print(form.errors)
    context = {
        'cart_items': cart_items,
        'cart_count': cart_count,
    }
    return render(request, 'orders/place_order.html', context)
