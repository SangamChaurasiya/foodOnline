from django.urls import path
from marketplace import views


app_name = 'marketplace'

urlpatterns = [
    path('', views.marketplace, name="marketplace"),
    path('<slug:vendor_slug>/', views.vendor_details, name="vendor_details"),
]
