from django.urls import path
from . import views

urlpatterns=[
    path('',views.home,name='home'),
    path('search',views.search,name='search'),
    path('add_products',views.add_products,name='add_products'),
    path('product_desc/<pk>',views.product_desc,name='product_desc'),
    path('cart',views.cart,name='cart'),
    path('add_to_cart/<pk>',views.add_to_cart,name='add_to_cart'),
    path('cart',views.cart,name='cart'),
    path('add_item/<int:pk>',views.add_item,name='add_item'),
    path('remove_item/<int:pk>',views.remove_item,name = 'remove_item'),
    path('checkout',views.checkout,name='checkout'),
    path('payment',views.payment,name='payment'),
    path('handlerequest',views.handlerequest,name='handlerequest'),
    path('Invoice',views.Invoice,name='Invoice'),
]