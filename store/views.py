
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from TemuBlitzDjango import settings
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from .models import OrderItem
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

    # Calculate subtotal = sum of (price * quantity)
    subtotal = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())

    shipping_fee = Decimal('50.00')  # fixed shipping fee

    total = subtotal + shipping_fee

    context = {
        'cart': cart,
        'subtotal': subtotal,
        'shipping_fee': shipping_fee,
        'total': total,
    }

    return render(request, 'store/cart.html', context)

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
    shipping_fee = Decimal('50.00')
    total += shipping_fee

    if request.method == 'POST':
        name = request.POST.get('name')
        email_address = request.POST.get('email')  # avoid variable name conflict
        address = request.POST.get('address')

        # Create the order
        order = Order.objects.create(
            customer_name=name,
            email=email_address,
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

        # Prepare and send email
        html_message = render_to_string('store/order_confirmation_message.html', {
            'name': name,
            'items': order.items.all(),
            'shipping_fee': f"{shipping_fee:.2f}",
            'total': f"{total:.2f}",
            'address': address,
        })

        email = EmailMultiAlternatives(
            subject='Order Confirmation',
            body='Thank you for your order.',
            from_email=settings.EMAIL_HOST_USER,
            to=[email_address]
        )
        email.attach_alternative(html_message, "text/html")
        email.send()

        # Clear cart and show confirmation
        request.session['cart'] = {}
        return render(request, 'store/order_confirmation.html', {'order': order})

    return render(request, 'store/checkout.html', {'cart': cart, 'total': total, 'shipping_fee': shipping_fee})

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