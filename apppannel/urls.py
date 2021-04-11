from django.contrib import admin
from django.urls import path
from django.conf import settings
from apppannel import views
from django.views.generic.base import RedirectView

urlpatterns = [
     path('login', views.loginadmin, name='login'),
     path('', RedirectView.as_view(url='login')),
     path('adminlogout', views.logoutadmin, name='adminlogout'),
     path('dashboard', views.admindashboard, name='admindashboard'),
     path('manage-products', views.manageproducts, name='manageproducts'),
     path('add-product', views.addproduct, name='addproduct'),
     path('change-product-status', views.changestatus, name='changestatus'),
     path('edit-product/<int:product_id>', views.editproduct, name='editproduct'),
     path('delete-product/<int:product_id>', views.deleteproduct, name='deleteproduct'),
     path('manage-users', views.manageusers, name='manageusers'),
     path('admin-view-reports', views.adminviewreports, name='adminviewreports'),
     path('todayssalesreport', views.todayssalesreport, name='todayssalesreport'),
     ]