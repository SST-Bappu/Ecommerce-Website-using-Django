import json
from .models import *

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    items = []
    order = {'get_cart_total':0, 'get_cart_items':0,'shipping':False}
    for i in cart:
        try:
            order['get_cart_items']+=cart[i]['quantity']
            product = Product.objects.get(id=i)
            total = product.price * cart[i]['quantity']
            order['get_cart_total']+=total
            item ={
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageURL,
                    },
                'quantity':cart[i]['quantity'],
                'get_total':total,
                }
            items.append(item)
            if product.digital == False:
                order['shipping'] = True
        except:
            pass
    cartItems = order['get_cart_items']
    return {'order':order,'items':items,'cartItems':cartItems}


def GuestOrder(request,data):
    cookieData = cookieCart(request)
    name = data['UserInfo']['name']
    email = data['UserInfo']['email']
    customer,created = Customer.objects.get_or_create(email = email)
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer = customer,
        complete = False,
    )
    items = cookieData['items']
    for item in items:
        product = Product.objects.get(id = item['product']['id'])
        OrderItem.objects.create(
            product = product,
            order = order,
            quantity = item['quantity'],
        )
    return order,customer