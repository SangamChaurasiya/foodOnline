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

    # Fooditem CRUD
    path('menu-builder/food/add/', VendorViews.add_food, name="add_food"),
    path('menu-builder/food/edit/<int:pk>/', VendorViews.edit_food, name="edit_food"),
    path('menu-builder/food/delete/<int:pk>/', VendorViews.delete_food, name="delete_food"),

    # Opening Hour CRUD
    path('opening-hours/', VendorViews.opening_hours, name="opening_hours"),
    path('opening-hours/add/', VendorViews.add_opening_hours, name="add_opening_hours"),
    path('opening-hours/remove/<int:id>/', VendorViews.remove_opening_hours, name="remove_opening_hours"),

]
