from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm
# Create your views here.
def store(request):
    products = Product.objects.all()
    return render(request, 'store/store.html', {'products': products})



# ➕ Add item to cart (stored in session)
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1,
            'image_url': product.image.url if product.image else '',
        }

    request.session['cart'] = cart
    return redirect('view_cart')


# 🛒 View cart contents
def view_cart(request):
    cart = request.session.get('cart', {})
    total = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())
    return render(request, 'store/cart.html', {'cart': cart, 'total': total})

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart  # Save changes
        messages.success(request, "Item removed from cart.")
    else:
        messages.warning(request, "Item not found in cart.")

    return redirect('view_cart')  # Redirect to cart page


def update_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        quantity = int(request.POST.get('quantity', 1))

        if quantity < 1:
            cart.pop(str(product_id), None)  # Remove item if quantity is invalid
            messages.info(request, "Item removed from cart.")
        else:
            if str(product_id) in cart:
                cart[str(product_id)]['quantity'] = quantity
                messages.success(request, "Quantity updated.")

        request.session['cart'] = cart
    return redirect('view_cart')

# ❌ Clear cart
def clear_cart(request):
    request.session['cart'] = {}
    return redirect('store')


# ✅ Checkout form
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('store')

    total = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')

        order = Order.objects.create(
            customer_name=name,
            email=email,
            address=address,
            total=total
        )

        for item in cart.values():
            OrderItem.objects.create(
                order=order,
                product_name=item['name'],
                quantity=item['quantity'],
                price=item['price']
            )

        request.session['cart'] = {}
        return render(request, '', {'order': order})

    return render(request, 'store/checkout.html', {'cart': cart, 'total': total})

def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('store')
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('store')  # Redirect to the login page after successful registration
    else:
        form = RegisterForm()

    return render(request, 'store/register.html', {'form': form})

def login_user(request):

    # Login Function is build in navbar
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect based on user type
            if user.is_staff:
                return redirect('/admin/')
            else:
                return redirect('store')  # Replace with your desired URL name
        else:
            return render(request, 'store/login.html', {'error': 'Invalid credentials'})
    return render(request, 'store/store.html')