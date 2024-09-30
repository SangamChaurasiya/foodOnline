from django.urls import path
from customers import views
from accounts import views as AccountViews

app_name = "customer"

urlpatterns = [
    path('', AccountViews.customerDashboard, name="customer"),
    path('profile/', views.cprofile, name="cprofile"),
    path('my_orders/', views.my_orders, name="customer_my_orders"),
    path('order_details/<int:order_number>/', views.order_details, name="customer_order_details"),
]
