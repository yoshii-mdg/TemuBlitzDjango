
from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
# Create your views here.
def store(request):
    products = Product.objects.all()
    users = User.objects.all()
    context = {'products': products, 'users': users}

    #Login Function is build in navbar
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
    return render(request, 'store/store.html', context)

def cart(request):
    context = {}
    return render(request, 'store/cart.html', context)


def checkout(request):
    context = {}
    return render(request, 'store/checkout.html', context)

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

def login(request):
    pass