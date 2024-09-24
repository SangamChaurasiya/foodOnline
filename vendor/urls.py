from django.urls import path
from vendor import views as VendorViews
from accounts import views as AccountViews

app_name = 'vendor'

urlpatterns = [
    path('', AccountViews.myAccount),
    path('registerVendor/', VendorViews.registerVendor, name="registerVendor"),
    path('vendorDashboard/', VendorViews.vendorDashboard, name="vendorDashboard"),
    path('profile/', VendorViews.vprofile, name="vprofile"),
    path('menu-builder/', VendorViews.menu_builder, name="menu_builder"),
    path('menu-builder/category/<int:pk>/', VendorViews.fooditems_by_category, name="fooditems_by_category"),

    # Category CRUD
    path('menu-builder/category/add/', VendorViews.add_category, name="add_category"),
    path('menu-builder/category/edit/<int:pk>/', VendorViews.edit_category, name="edit_category"),
    path('menu-builder/category/delete/<int:pk>/', VendorViews.delete_category, name="delete_category"),

]
