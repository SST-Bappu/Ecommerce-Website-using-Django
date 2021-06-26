from django.urls import path
from . import views

urlpatterns=[
    path('',views.store,name="store"),
    path('cart/',views.cart,name='cart'),
    path('checkout/',views.checkout,name='checkout'),
    path('updateItem/',views.updateItem, name='updateItem'),
    path('processOrder/',views.processOrder,name='processOrder'),
    path('userLogin/',views.UserLogin,name='userLogin'),
    path('userLogout/',views.UserLogout,name='userLogout'),
    path('userRegistration/',views.UserRegistration,name='userRegistration'),
    path('orderRecords/',views.OrderRecords,name='orderRecords'),
]