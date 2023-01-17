from django.shortcuts import render, redirect
from main.forms import *
from .models import *
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.http import HttpResponse

razorpay_client =razorpay.Client(auth=(settings.RAZORPAY_ID,settings.RAZORPAY_SECRET))

# hmoe view code >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def home(request):
    products = Product.objects.all()
    category = Category.objects.all()
    return render(request, 'index.html', {'pr': products,'ct':category})

# search code >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def search(request):
    prodt= None
    query= None
    if 'q' in request.GET:
        query=request.GET.get('q')
        prodt=Product.objects.all().filter(Q(name__contains=query)|Q(desc__contains=query))

    return render(request,'search.html',{'qr':query,'pr':prodt})

# add-product admin code >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def add_products(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('add_products')
        else:
            messages.info(request, "product is not added ,try again ")
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

# product detail code >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def product_desc(request, pk):
    product = Product.objects.get(pk=pk)
    return render(request, 'product_detail.html', {'pr': product})

# product add-to-cart >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def add_to_cart(request, pk):
    # get the product id = pk
    product = Product.objects.get(pk=pk)

    # create order item
    order_item, created = OrderItem.objects.get_or_create(
        product=product,
        user=request.user,
        ordered=False,
    )

    # get query set of order object of user
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk=pk).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "added quantity item")
            return redirect("product_desc", pk=pk)
        else:
            order.items.add(order_item)
            messages.info(request, "item add to cart")
            return redirect("product_desc", pk=pk)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "item added to cart")
        return redirect('product_desc', pk=pk)


def cart(request):
    if Order.objects.filter(user=request.user, ordered=False).exists():
        order = Order.objects.get(user=request.user, ordered=False)
        return render(request, 'cart.html', {'order': order})
    return render(request, 'cart.html', {'message': "Your Cart Is Empty"})

# product add-count >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>..

def add_item(request, pk):
    product = Product.objects.get(pk=pk)

    # create order item
    order_item, created = OrderItem.objects.get_or_create(
        product=product,
        user=request.user,
        ordered=False,
    )

    # get query set of order object of user
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk=pk).exists():
            if order_item.quantity < product.product_available_count:
                order_item.quantity += 1
                order_item.save()
                messages.info(request, "added quantity item")
                return redirect("cart")
            else:
                messages.info(request, "Sorry! product is out of stock")
                return redirect('cart')
        else:
            order.items.add(order_item)
            messages.info(request, "item add to cart")
            return redirect("product_desc", pk=pk)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "item added to cart")
        return redirect('product_desc', pk=pk)

# product count remove >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def remove_item(request, pk):
    item = get_object_or_404(Product, pk=pk)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False,
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk=pk).exists():
            order_item = OrderItem.objects.filter(
                product=item,
                user=request.user,
                ordered=False,
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order_item.delete()
            messages.info(request, "item quantity was update ")
            return redirect('cart')
        else:
            messages.info(request, "this is item not your cart")
            return redirect('cart')
    else:
        messages.info(request, "you Do not have any order")
        return redirect('cart')

# checkout >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def checkout(request):
    if CheckoutAddress.objects.filter(user=request.user).exists():
        return render(request, 'checkout.html', {'payment_allow': 'allow'})
    if request.method == 'POST':
       form = Checkoutform(request.POST)
       if form.is_valid():
           street_address = form.cleaned_data.get('street_address')
           apartment_address = form.cleaned_data.get('apartment_address')
           country = form.cleaned_data.get('country')
           zip_code = form.cleaned_data.get('zip_code')

           checkout_address = CheckoutAddress(
               user=request.user,
               street_address=street_address,
               apartment_address=apartment_address,
               country=country,
               zip_code=zip_code,
           )
           checkout_address.save()
           print("It should render the summary page")
           return render(request, 'checkout.html', {'payment_allow': 'allow'})
        # except Exception as e:
        # messages.warning(request, 'Failed checkout')
        # return redirect('checkout')

    else:
        form = Checkoutform()
        return render(request, 'checkout.html', {'form': form})

# payment >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def payment(request):
    try:
        order =Order.objects.get(user=request.user,ordered=False)
        address =CheckoutAddress.objects.get(user=request.user)
        order_amount =order.get_total_price()
        order_currency="INR"
        order_receipt= order.ordered_id
        notes = {
            'street_address':address.street_address,
            'apartment_address':address.apartment_address,
            'country':address.country.name,
            'zip_code':address.zip_code,
        }
        razorpay_order = razorpay_client.order.create(
            dict(
                amount =order_amount * 100,
                currency = order_currency,
                receipt =order_receipt,
                notes=notes,
                payment_capture ="0",
            )
        )
        print(razorpay_order["id"])
        order.razorpay_order_id=razorpay_order["id"]
        order.save()
        print('it should render the summary page ')
        return render(
            request,
            "paymentsummaryrazorpay.html",
            {
                "order":order,
                "order_id":razorpay_order["id"],
                "orderId" :order.ordered_id,
                "final_price":order_amount,
                "razorpay_merchant_id":settings.RAZORPAY_ID,
            },
        )
    except Order.DoesNotExist:
        print("order not fount")
        return HttpResponse("404 error")

# call back funaction >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

@csrf_exempt
def handlerequest(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get("razorpay_payment_id", "")
            order_id = request.POST.get("razorpay_order_id", "")
            signature = request.POST.get("razorpay_signature", "")
            print(payment_id, order_id, signature)
            params_dict = {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }

            try:
                order_db = Order.objects.get(razorpay_order_id=order_id)
                print("Order Found")
            except:
                print("Order Not found")
                return HttpResponse("505 Not Found")
            order_db.razorpay_payment_id = payment_id
            order_db.razorpay_signature = signature
            order_db.save()
            print("Working............")
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result == None:
                print("Working Final Fine............")
                amount = order_db.get_total_price()
                amount = amount * 100  # we have to pass in paisa
                payment_status = razorpay_client.payment.capture(payment_id, amount)
                if payment_status is not None:
                    print(payment_status)
                    order_db.ordered = True
                    order_db.save()
                    print("Payment Success")
                    checkout_address = CheckoutAddress.objects.get(user=request.user)
                    request.session[
                        "order_complete"
                    ] = "Your Order is Successfully Placed, You will receive your order within 5-7 working days"
                    return render(request, "Invoice.html",{"order":order_db,"payment_status":payment_status,"checkout_address":checkout_address})
                else:
                    print("Payment Failed")
                    order_db.ordered = False
                    order_db.save()
                    request.session[
                        "order_failed"
                    ] = "Unfortunately your order could not be placed, try again!"
                    return redirect("/")
            else:
                order_db.ordered = False
                order_db.save()
                return render(request, "paymentfailed.html")
        except:
            return HttpResponse("Error Occured")

# invoice >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def Invoice(request):
    return render(request, "Invoice.html")