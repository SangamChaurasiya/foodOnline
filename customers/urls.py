from django.urls import path
from customers import views
from accounts import views as AccountViews

app_name = "customer"

urlpatterns = [
    path('', AccountViews.customerDashboard, name="customer"),
    path('profile/', views.cprofile, name="cprofile"),
]
