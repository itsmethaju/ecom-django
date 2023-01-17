from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from main.models import *
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
# Create your views here.
def user_login(request):
    if request.method == "POST":
       username = request.POST.get('username')
       password = request.POST.get('password')
       user = authenticate(username=username,password=password)
       if user is not None:
            login(request,user)
            return redirect('/')
       messages.info(request,'User Login Failed Pleas Try Again ..')


    return render(request,'login.html')

def user_register(request):
    if request.method == "POST":
        username=request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password =request.POST.get('confirm_password')
        
        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.info(request,'User Name Already Created')
                return redirect('user_register')
            else:
                if User.objects.filter(email=email).exists():
                   messages.info(request,'Email Already Exist')
                   return redirect('user_register')
                else:
                    user = User.objects.create_user(username=username,email=email,password=password)
                    user.save()
                    
                    # code for login user will come here
                    our_user = authenticate(username=username,password=password)
                    if our_user is not None:
                        login(request,user)
                        return redirect('/')
        else:
            messages.info(request,"password and confirm password mismatch!")
            return redirect('user_register')

    return render(request,'register.html')

def user_logout(request):
   logout(request)
   return redirect('/')