from django.views.decorators.csrf import csrf_protect
from django.core.checks import messages
from django.shortcuts import redirect, render
from django.http import JsonResponse
import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import *
from .utils import cookieCart, GuestOrder
from .form import CreateUserForm
import datetime
# Create your views here.

def home(request):
    store(request)
def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
        cartItems = cookieData['cartItems']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
        cartItems = cookieData['cartItems']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print("Product ID=", productId)
    print("Action = ", action)
    customer = request.user.customer
    print(customer)
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    order_item, created = OrderItem.objects.get_or_create(
        order=order, product=product)
    if action == 'add':
        order_item.quantity += 1
    elif action == 'remove':
        order_item.quantity -= 1
    order_item.save()
    if order_item.quantity <= 0:
        order_item.delete()
    return JsonResponse("Data is added", safe=False)


# These two lines below are placed so that the website work fine in InCognito Mode


@csrf_protect
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)

    else:
        order, customer = GuestOrder(request, data)

    order.transaction_id = transaction_id
    total = float(data['UserInfo']['total'])
    if total == float(order.get_cart_total):
        order.complete = True
    order.save()
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['ShippingInfo']['address'],
            city=data['ShippingInfo']['city'],
            state=data['ShippingInfo']['state'],
            zipcode=data['ShippingInfo']['zipcode']
        )

    return JsonResponse("Payment has been completed", safe=False)


# Login Process
def UserLogin(request):
    context = {}
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('store')
        else:
            messages.info(request, "Username or Password is incorrect!")
    return render(request, 'store/loginForm.html', context)


def UserLogout(request):
    logout(request)
    return redirect('store')


def UserRegistration(request):
    form = CreateUserForm()
    context = {'form': form}
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            Customer.objects.create(
                user=user,
                name=username,
                email=email,
            )
            messages.success(
                request, 'User account has been created for'+username)
            return redirect('userLogin')
        else:
            pass1 = form.cleaned_data.get('password1')
            pass2 = form.cleaned_data.get('password2')
            if pass1 != pass2:
                messages.error(request, "Password didn't match")
            else:
                messages.error(request, "Fill all the field correctly")
            return redirect('userRegistration')
    return render(request, 'store/userRegistration.html', context)


@login_required(login_url="userLogin")
def OrderRecords(request):
    if request.user.is_authenticated:
        Customer = request.user.customer
        Curorder, created = Order.objects.get_or_create(
            customer=Customer, complete=False)
        cartItems = Curorder.get_cart_items
        orders = Customer.order_set.all()
        orderRecords = []
        for order in orders:
            items = order.orderitem_set.all()
            cart_items = order.get_cart_items
            cart_total = order.get_cart_total
            records = {
                'date': order.date_ordered,
                'items': items,
                'cart_items': cart_items,
                'cart_total': cart_total,
                'items': items
            }
            orderRecords.append(records)
        context = {'records': orderRecords, 'cartItems': cartItems}

    return render(request, 'store/orderRecords.html', context)
