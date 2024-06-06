from django.urls import path
from accounts import views

app_name = 'accounts'
urlpatterns = [
    path('registerUser/', views.registerUser, name="registerUser"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('myAccount/', views.myAccount, name="myAccount"),
    path('customerDashboard/', views.customerDashboard, name="customerDashboard"),
    path('activate/<uidb64>/<token>/', views.activate, name="activate"),
    path('forgotPassword/', views.forgotPassword, name="forgotPassword"),
    path('resetPasswordValidate/<uidb64>/<token>/', views.resetPasswordValidate, name="resetPasswordValidate"),
    path('resetPassword/', views.resetPassword, name="resetPassword"),
]
