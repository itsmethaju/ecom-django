from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.urls import reverse
from django_countries.fields import CountryField



class Category(models.Model):
    category_name =models.CharField(max_length=255)

    def __str__(self):
        return self.category_name

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    desc = models.TextField()
    price = models.FloatField(default = 0.0)
    product_available_count = models.IntegerField(default = 0)
    img = models.ImageField(upload_to='Product')

    def get_add_to_cart_url(self):
        return reverse('add_to_cart',kwargs ={
            'pk':self.pk
        })
    def __str__(self):
        return self.name

class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default = False)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    quantity = models.IntegerField(default = 1)


    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

    def get_total_item_price(self):
        return self.quantity * self.product.price

    def get_final_price(self):
        return self.get_total_item_price()

class Order(models.Model):
    user= models.ForeignKey(User, on_delete = models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default =False)
    ordered_id = models.CharField(max_length = 100,unique=True,default = None,blank =True,null = True)
    date_of_payment = models.DateTimeField(auto_now_add = True)
    order_delivered = models.BooleanField(default = False)
    order_received = models.BooleanField(default = False)
    # checkout_address=models.ForeignKey(CheckoutAddress,on_delete = models.CASCADE)
    razorpay_order_id = models.CharField(max_length =500,null=True,blank = True)
    razorpay_payment_id = models.CharField(max_length =500,null=True,blank =True)
    razorpay_signature = models.CharField(max_length=500,null=True,blank =True)


    def save(self,*args,**kwargs):
        if self.ordered_id is None and self.date_of_payment and self.id:
            self.ordered_id = self.date_of_payment.strftime('PAY2ME%y%m%d0DR')+str(self.id)

        return super().save(*args,**kwargs)

    def __str__(self):
        return self.user.username

    def get_total_price(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total
    def get_total_count(self):
        order = Order.objects.get(pk=self.pk)
        return order.items.count()

class CheckoutAddress(models.Model):
    user = models.ForeignKey(User,on_delete =models.CASCADE)
    street_address =models.CharField(max_length =100)
    apartment_address =models.CharField(max_length =100)
    zip_code = models.CharField(max_length=15)
    country = CountryField(multiple =False)


    def __str__(self):
        return self.user.username