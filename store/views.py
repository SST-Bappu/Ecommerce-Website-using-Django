from django.shortcuts import render
from django.http import JsonResponse
import json
from .models import *
from .utils import cookieCart
import datetime
# Create your views here.
def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']

    products = Product.objects.all()
    context ={'products':products,'cartItems':cartItems}
    return render(request,'store/store.html',context)
    
def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
        cartItems = cookieData['cartItems']
        
        
    context ={'items':items,'order':order,'cartItems':cartItems}
    return render(request,'store/cart.html',context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order,created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
        cartItems = cookieData['cartItems']

    context ={'items':items,'order':order,'cartItems':cartItems}
    return render(request,'store/checkout.html',context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print("Product ID=",productId)
    print("Action = ",action)
    customer = request.user.customer
    print(customer)
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    order_item,created = OrderItem.objects.get_or_create(order=order, product=product)
    if action == 'add':
        order_item.quantity +=1
    elif action=='remove':
        order_item.quantity -=1
    order_item.save()
    if order_item.quantity<=0:
        order_item.delete()
    return JsonResponse("Data is added",safe=False)

#These two lines below are placed so that the website work fine in InCognito Mode
from django.views.decorators.csrf import csrf_protect
@csrf_protect
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order,created = Order.objects.get_or_create(customer=customer,complete=False)
        total = float(data['UserInfo']['total'])
        order.transaction_id = transaction_id
        if total == float(order.get_cart_total):
            order.complete = True
        order.save()
        if order.shipping == True:
            ShippingAddress.objects.create(
                customer = customer,
                order = order,
                address = data['ShippingInfo']['address'],
                city = data['ShippingInfo']['city'],
                state = data['ShippingInfo']['state'],
                zipcode = data['ShippingInfo']['zipcode'],
            )
    else:
        print("User isn't logged in....")

    return JsonResponse("Payment has been completed",safe=False)