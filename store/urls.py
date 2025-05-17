from django.urls import path
from . import views
from store.views import login_user
urlpatterns = [
    path('', views.store, name='store'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register, name='register'),
    path('login/', login_user, name='login')
]