from django.contrib import admin
from orders.models import Payment, Order, OrderedFood


admin.site.register(Payment)
admin.site.register(Order)
admin.site.register(OrderedFood)
