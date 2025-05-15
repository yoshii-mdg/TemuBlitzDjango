from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib import admin
urlpatterns = [
    path('', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
]