from django.urls import path
from accounts import views

app_name = 'accounts'
urlpatterns = [
    path('registerUser/', views.registerUser, name="registerUser"),
]
