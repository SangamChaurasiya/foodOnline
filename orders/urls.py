from django.urls import path
from orders import views


app_name = 'orders'

urlpatterns = [
    path('place-order/', views.place_order, name="place_order"),
    path('payments/', views.payments, name="payments"),
    path('order_complete/', views.order_complete, name="order_complete"),
]
