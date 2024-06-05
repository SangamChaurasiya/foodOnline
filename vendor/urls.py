from django.urls import path
from vendor import views

app_name = 'vendor'

urlpatterns = [
    path('registerVendor/', views.registerVendor, name="registerVendor"),
]
