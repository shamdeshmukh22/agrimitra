"""
URL configuration for Agri project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from agriapp import views

urlpatterns = [
    path('',views.HomePage),
    path('login/',views.LoginUser),
    path('logout/',views.logout_view),
    path('sign-up/',views.signUp),
    path('services/',views.Services),
    path('equipment/',views.Equipmentpage),
    path('add-equipment/',views.AddEquipment),
    path('your-performerce/',views.YourPerformerce),
    path('My-equipment/',views.MyEquipment),
    path('view-more/<int:id>/',views.view_more,name='view-more'),
    path('edit-my-equipment/<int:id>/',views.edit_my_equipment,name='edit-my-equipment'),
    path('delete-my-equipment/<int:id>/',views.delete_my_equipment,name='delete-my-equipment'),
    path('rent-now/<int:id>/',views.rent_now,name='rent-now'),
    path('owner-requests/',views.owner_requests,name='owner_requests'),
    path('approve-request/<int:order_id>/',views.approve_request,name='approve_request'),
    path('reject-request/<int:order_id>/',views.reject_request,name='reject_request'),
    path('customer-orders/',views.customer_orders,name='customer_orders'),
    path('cancel-order/<int:order_id>/',views.cancel_order,name='cancel_order'),
    path('process-payment/<int:order_id>/',views.process_payment,name='process_payment'),
    path('payment-success/<int:order_id>/',views.payment_success,name='payment_success'),
    path('admin/', admin.site.urls),
]
