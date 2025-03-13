from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, CartItem, Order, OrderItem  # Ensure Order and OrderItem are imported

# --- AUTHENTICATION VIEWS ---
def login_view(request):
    """Handles user login."""
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirects to home after login
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})

def register_view(request):
    """Handles user registration."""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically logs in the user
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})

@login_required
def logout_view(request):
    """Logs out the user."""
    logout(request)
    return redirect('home')

# --- PRODUCT & CART VIEWS ---
def home(request):
    """Homepage displaying all products."""
    products = Product.objects.all()  # Fetch all products from the database
    return render(request, 'store/home.html', {'products': products})

@login_required
def cart_view(request):
    """Displays items in the user's cart."""
    cart_items = CartItem.objects.filter(user=request.user)
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total_amount': total_amount})

@login_required
def add_to_cart(request, product_id):
    """Adds a product to the cart."""
    product = Product.objects.get(id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    """Removes a product from the cart."""
    cart_item = CartItem.objects.get(id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')

# --- CHECKOUT & ORDER VIEWS ---
@login_required
def checkout(request):
    """Handles the checkout process."""
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect('cart')  # Redirect if the cart is empty

    total_amount = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == "POST":
        # Create a new order
        order = Order.objects.create(user=request.user, total_amount=total_amount)

        # Add order items
        OrderItem.objects.bulk_create([
            OrderItem(order=order, product=item.product, quantity=item.quantity)
            for item in cart_items
        ])

        cart_items.delete()  # Clear the cart after placing the order
        return redirect('order_history')

    return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total_amount': total_amount})

@login_required
def order_history(request):
    """Displays the order history of the logged-in user."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_history.html', {'orders': orders})
