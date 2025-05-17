from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from store.views import login_user
urlpatterns = [
    path('', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register, name='register'),
    path('login/', login_user, name='login')
]