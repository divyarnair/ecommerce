from django.shortcuts import render
from .forms import LoginForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy
from django.urls import reverse
from django.http import HttpResponseRedirect
from apppannel.models import Products
from apppannel.forms import ProductForm
from apppannel.forms import EditProductForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.models import User
import datetime
import csv


def checksuperuser(user):
    return user.is_superuser



def loginadmin(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('admindashboard') )
    else:	
        if request.method == 'POST':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data['username']
                password = login_form.cleaned_data['password']

                user = authenticate(username=username, password=password)
                                
                if user is not None:
                    if user.is_active and user.is_superuser:
                        login(request,user)	
                        return HttpResponseRedirect(reverse('admindashboard') )
                    else:
                        return HttpResponse('Your account is not active')
                else:
                    return HttpResponse('The Account does not exists')
            else:
                login_form = LoginForm()
                return render(request, "apppannel/partials/adminpannel/login.html",{"form":login_form})
        else:
            login_form = LoginForm()
        return render(request,'apppannel/partials/adminpannel/login.html',{"form":login_form})    


@user_passes_test(checksuperuser,login_url = reverse_lazy('login'))
def logoutadmin(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))

@user_passes_test(checksuperuser,login_url = reverse_lazy('login'))
def admindashboard(request):
    return render(request,'apppannel/partials/adminpannel/admindashboard.html',{})

@user_passes_test(checksuperuser,login_url = reverse_lazy('login'))
def manageproducts(request):
    products = Products.objects.all()
    return render(request,'apppannel/partials/adminpannel/manageproducts.html',{'products':products})

@user_passes_test(checksuperuser,login_url = reverse_lazy('login'))
def addproduct(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            product_name = product_form.cleaned_data['product_name']
            product_description = product_form.cleaned_data['product_description']
            price = product_form.cleaned_data['price']
            product_image = request.FILES['product_image']

            product_instance = Products(product_name = product_name, 
                                        product_description = product_description,
                                        price = price,
                                        product_picture = product_image)
            product_instance.save()
            return HttpResponseRedirect(reverse('manageproducts'))
        else:
            product_form = ProductForm(request.POST, request.FILES)
            return render(request,'apppannel/partials/adminpannel/addproduct.html',{'productform':product_form}) 
    else:
        product_form = ProductForm()
        return render(request,'apppannel/partials/adminpannel/addproduct.html',{'productform':product_form})    

@csrf_exempt
@user_passes_test(checksuperuser,login_url = reverse_lazy('login'))
def changestatus(request):
    if request.is_ajax():
        product_id = int(request.POST['product'])
        action = request.POST['action']
        product_instance = Products.objects.get(id=product_id)
        if action == "disable":
            product_instance.is_active = 0
        else:
            product_instance.is_active = 1
        product_instance.save()
        return JsonResponse({'result':'success'})   

@user_passes_test(checksuperuser,login_url = reverse_lazy('login'))
def editproduct(request,product_id):

    if request.method == 'POST':
        product_form = EditProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            product_name = product_form.cleaned_data['product_name']
            product_description = product_form.cleaned_data['product_description']
            price = product_form.cleaned_data['price']
            

            product_instance = Products.objects.get(id=product_id)
            product_instance.product_name = product_name
            product_instance.product_description = product_description
            product_instance.price = price
            if request.FILES:
                product_image = request.FILES['product_image']
                product_instance.product_picture = product_image
            product_instance.save()
            return HttpResponseRedirect(reverse('manageproducts'))
        else:
            product_form = EditProductForm(request.POST, request.FILES)
            return render(request,'apppannel/partials/adminpannel/editproduct.html',{'productform':product_form}) 
    else:
        product_instance = Products.objects.get(id=product_id)
        product_form = EditProductForm(initial={'product_name': product_instance.product_name,
                                            'product_description':product_instance.product_description,
                                            'price':product_instance.price,
                                            'product_image':product_instance.product_picture
                                            })
        return render(request,'apppannel/partials/adminpannel/editproduct.html',{'productform':product_form,'current_image':product_instance.product_picture})
@user_passes_test(checksuperuser,login_url = reverse_lazy('login'))
def deleteproduct(request,product_id):
    product_instance = Products.objects.get(id=product_id)
    product_instance.delete()
    return HttpResponseRedirect(reverse('manageproducts'))       

@user_passes_test(checksuperuser,login_url = reverse_lazy('login'))
def manageusers(request):
    users = User.objects.filter(is_superuser = 0,is_staff = 0)
    return render(request,'apppannel/partials/adminpannel/manageusers.html',{'users':users})
    
@user_passes_test(checksuperuser,login_url = reverse_lazy('login'))
def adminviewreports(request):
    return render(request,'apppannel/partials/adminpannel/adminreports.html',{})


@user_passes_test(checksuperuser,login_url = reverse_lazy('login'))
def todayssalesreport(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="salesreport"'+str(datetime.date.today())+'".csv"'
    writer = csv.writer(response)
    today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
    sales = CustomerCheckout.objects.filter(payedon__range=(today_min, today_max))
    writer.writerow(['Order_id', 'Payment_id', 'Amount', 'Reciept', 'Phonenum', 'Address'])
    for sale in sales:
        writer.writerow([sale.order_id, sale.payment_id, sale.total_amount, sale.reciept_num, sale.delivery_phone, sale.delivery_address])
    return response     