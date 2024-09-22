from django.urls import path
from vendor import views as VendorViews
from accounts import views as AccountViews

app_name = 'vendor'

urlpatterns = [
    path('', AccountViews.myAccount),
    path('registerVendor/', VendorViews.registerVendor, name="registerVendor"),
    path('vendorDashboard/', VendorViews.vendorDashboard, name="vendorDashboard"),
    path('profile/', VendorViews.vprofile, name="vprofile"),
]
