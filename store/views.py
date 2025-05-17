from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CheckoutForm

from .models import Product, Order, OrderItem
from .forms import RegisterForm


def store(request):
    """Display all products in the store."""
    products = Product.objects.all()
    return render(request, 'store/store.html', {'products': products})


def add_to_cart(request, product_id):
    """Add a product to the session cart or increment quantity if already present."""
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
    messages.success(request, f'Added {product.name} to cart.')
    return redirect('view_cart')


def view_cart(request):
    """Display current cart contents with totals."""
    cart = request.session.get('cart', {})

    subtotal = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())
    shipping_fee = Decimal('50.00')
    total = subtotal + shipping_fee

    context = {
        'cart': cart,
        'subtotal': subtotal,
        'shipping_fee': shipping_fee,
        'total': total,
    }
    return render(request, 'store/cart.html', context)


def remove_from_cart(request, product_id):
    """Remove an item from the cart."""
    cart = request.session.get('cart', {})
    product_str_id = str(product_id)

    if product_str_id in cart:
        removed_name = cart[product_str_id]['name']
        del cart[product_str_id]
        request.session['cart'] = cart
        messages.success(request, f"Removed {removed_name} from cart.")
    else:
        messages.warning(request, "Item not found in cart.")

    return redirect('view_cart')


def update_cart(request, product_id):
    """Update the quantity of a specific product in the cart."""
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            messages.error(request, "Invalid quantity.")
            return redirect('view_cart')

        product_str_id = str(product_id)
        if quantity < 1:
            cart.pop(product_str_id, None)
            messages.info(request, "Item removed from cart.")
        elif product_str_id in cart:
            cart[product_str_id]['quantity'] = quantity
            messages.success(request, "Quantity updated.")

        request.session['cart'] = cart

    return redirect('view_cart')


def clear_cart(request):
    """Empty the cart completely."""
    request.session['cart'] = {}
    messages.info(request, "Cart cleared.")
    return redirect('store')


from .forms import CheckoutForm

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect('store')

    subtotal = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())
    shipping_fee = Decimal('50.00')
    total = subtotal + shipping_fee

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            order = Order.objects.create(
                customer_name=f"{data['first_name']} {data['last_name']}",
                email=data['email'],
                address=data['address'],
                total=total
            )

            items_summary = ""
            for item in cart.values():
                OrderItem.objects.create(
                    order=order,
                    product_name=item['name'],
                    quantity=item['quantity'],
                    price=item['price']
                )
                items_summary += f"{item['name']} × {item['quantity']} - ₱{item['price']}\n"

            request.session['cart'] = {}

            subject = "Order Confirmation - JewelLuxury"
            message = f"""Dear {data['first_name']},

Thank you for your purchase!

Order Summary:
{items_summary}
Shipping: ₱{shipping_fee}
Total: ₱{total}

We will deliver to:
{data['address']}

Notes: {data['additional_info']}

If you have questions, contact us at {settings.DEFAULT_FROM_EMAIL}.

Sincerely,
Temublitz Team
"""
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [data['email']], fail_silently=False)
                messages.success(request, "Order placed successfully! Confirmation email sent.")
            except Exception as e:
                messages.error(request, f"Order placed but failed to send email: {e}")

            return render(request, 'store/order_confirmation.html', {'order': order})

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = CheckoutForm()

    context = {
        'cart': cart,
        'total': total,
        'form': form
    }
    return render(request, 'store/checkout.html', context)

def logout_user(request):
    """Logout the user and redirect to store."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('store')


def register(request):
    """Register new user."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('store')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, 'store/register.html', {'form': form})


def login_user(request):
    """Login existing user."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('/admin/')
            else:
                return redirect('store')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'store/login.html')
