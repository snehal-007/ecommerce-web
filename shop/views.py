from django.shortcuts import render ,redirect
from django.http import HttpResponse
from .models import Product, Contact ,Orders ,OrderUpdate
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate ,login ,logout
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from paytm.checksum import verify_checksum
from paytm import checksum
from OnlineShop.settings import EMAIL_HOST_USER
from django.core.mail import send_mail


MERCHANT_KEY = 'T8zzzhsts0pIzKtE'

# Create your views here.

def index(request):
    # products = Product.objects.all()
    # print(products)
    
    allProds = []
    catprods = Product.objects.values('category','id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nslides = n//4 + ceil((n/4)-(n//4))
        allProds.append([prod,range(1,nslides),nslides])

    params = {'allProds':allProds}            
    return render(request,'shop/index.html',params)

def searchMatch(query,item):
    # return true only if query match the item
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True

    else:

        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category','id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query ,item)]


        n = len(prod)
        nslides = n//4 + ceil((n/4)-(n//4))
        if len(prod) != 0:
            allProds.append([prod,range(1,nslides),nslides])

    params = {'allProds':allProds,"msg":""}
    if len(allProds) == 0 or len(query)<4:
        params = {'msg':'Please make sure your Relevent Search Query'}  

    return render(request,'shop/search.html',params)

def about(request):
    return render(request,'shop/about.html')

def contact(request):
    if request.method == "POST":
        name = request.POST.get('uname','')
        email = request.POST.get('email','')
        phone = request.POST.get('phone','')
        desc = request.POST.get('desc','')
        print('uname=',name)
        print('email=',email)

        contact = Contact(name=name,email=email,phone=phone,desc=desc)
        contact.save()
     
        send_mail(name,desc,email,['bhoyasnehal08@gmail.com'],fail_silently=False)


        thank = True
        return render(request,'shop/checkout.html',{'thank':thank}) 
        
    return render(request,'shop/contact.html')

def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId','')
        email = request.POST.get('email','')
        print("order id",orderId)
        print("Email",email)

        try:
            order = Orders.objects.filter(order_id = orderId ,email = email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id = orderId)
                updates = []
                for item in update:
                    updates.append({'text':item.update_desc ,'time':item.timestamp})
                    response = json.dumps({"status":"success","updates":updates,"itemJson":order[0].items_json},default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"no items"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')  

    return render(request,'shop/tracker.html')


def productview(request,myid):
    # fetch the product using id
    product = Product.objects.filter(id=myid)
    return render(request,'shop/productview.html',{'product':product[0]})

def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson','')
        name = request.POST.get('name','')
        amount = request.POST.get('amount','')
        email = request.POST.get('email','')
        address = request.POST.get('address','') + " " + request.POST.get('address2','')
        city = request.POST.get('city','')
        state = request.POST.get('state','')
        phone = request.POST.get('phone','')
        zip_code = request.POST.get('zip_code','')

        orders = Orders(items_json=items_json,name=name,email=email,phone=phone,address=address,city=city,state=state,zip_code=zip_code,amount=amount)
        orders.save()
        update = OrderUpdate(order_id = orders.order_id ,update_desc = "The order has been placed")
        update.save()
        thank = True
        id = orders.order_id
        # return render(request,'shop/checkout.html',{'thank':thank,'id':id}) 
        
        # Request paytm to transfer the amount to your account after payment by user

        param_dict = {
            'MID':'NHIxiZ10508527091353',
            'ORDER_ID':str(orders.order_id),
            'TXN_AMOUNT':str(amount),
            'CUST_ID':'bhoyasnehal08@gmail.com',
            'INDUSTRY_TYPE_ID':'Retail',
            'WEBSITE':'WEBSTAGING',
            'CHANNEL_ID':'WEB',
	        'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',
        }

        param_dict['CHECKSUMHASH'] = checksum.generate_checksum(param_dict,MERCHANT_KEY)

        return render(request,'shop/paytm.html',{'param_dict':param_dict})


    return render(request,'shop/checkout.html')    

@ csrf_exempt
def handlerequest(request):
    # paytm will send you post request here

    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]
    print("response dict-",response_dict)
    # verify = checksum.verify_checksum(response_dict,MERCHANT_KEY,checksum)
    verify = verify_checksum(response_dict,MERCHANT_KEY,checksum)
    
    if verify:
        if response_dict['RESPCODE'] == '01':
            print("Order Successful")   

        else:
            print("Order unsuccessful because:"+response_dict['RESPMSG'])         

    return render(request,'shop/paymentstatus.html',{'response':response_dict})

def handleSignup(request):
    if request.method == 'POST':
        # Get the post parameters
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        # check for error input
        if len(username) > 10:
            messages.error(request,"Your username under 10 charecters please use more charecters")
            return redirect('ShopHome')

        if not username.isalnum():
            messages.error(request,"username should be letters and numbers")
            return redirect('ShopHome')    

        if pass1 != pass2:
            messages.error(request,"Your password is not match please check again")
            return redirect('ShopHome')    

        # Create user
        myuser = User.objects.create_user(username,email,pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()
        messages.success(request,"Your iCoder account has been successfully created")

        return redirect('ShopHome')

    else:
        return HttpResponse('404 Not Found')         

def handleLogin(request):
    if request.method == 'POST':
        loginusername = request.POST['loginUsername']
        loginpassword = request.POST['loginPassword']

        user = authenticate(username=loginusername ,password=loginpassword)
        
        if user is not None:
            login(request,user)
            messages.success(request,"Successfully Logged in")
            return redirect('ShopHome')

        else:
            messages.error(request,"Invalid Credentials, Please Try again")
            return redirect('ShopHome')    

    return HttpResponse('404 Not Found')

def handleLogout(request):
    logout(request)
    messages.success(request,"Successfully logged Out")
    return redirect('ShopHome')

     