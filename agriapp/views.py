from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from .forms import Sign_up,Login,EquipmentForm,RentalRequestForm,PaymentForm
from .models import User_Detail,Categories,Equipment,Orders
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q


def HomePage(req):
    user_id=req.session.get('user_id',-1)
    equipment=Equipment.objects.all()[:3]
    obj={
        'user_id':user_id,
          'equipment':equipment
    }
    return render(req,'home.html',{'obj':obj})



def LoginUser(req):
    if req.method == 'POST':
        email = req.POST.get('email')
        password = req.POST.get('password')
        form = Login()

        try:
            data = User_Detail.objects.get(email=email)

            if password == data.password:
                req.session['user_id'] = data.id
                return redirect("/")
            else:
                return render(req, 'Login.html', {
                    'form': form,
                    'error': 'Invalid password'
                })

        except User_Detail.DoesNotExist:
            return render(req, 'Login.html', {
                'form': form,
                'error': 'User not found'
            })

    else:
        form = Login()
        user_id=req.session.get('user_id',-1)
        obj={
            'user_id':user_id,
            'form':form
        }

    return render(req, 'Login.html', {'obj': obj})

def signUp(req):
    if req.method =='POST':
        form = Sign_up(req.POST)
        if form.is_valid():
            form.save()
            return redirect('/login')
    else:
        form = Sign_up()
        user_id=req.session.get('user_id',-1)
        obj={
            'user_id':user_id,
            'form':form
        }
    return render(req, 'SignUp.html', {'obj': obj})

def Services(req):
     user_id=req.session.get('user_id',-1)
     obj={
            'user_id':user_id,
        }
     return render(req,'Services.html',{'obj':obj})

def YourPerformerce(req):
    user_id=req.session.get('user_id',-1)
    if user_id==-1:
        return redirect("/login")
    else:
      data=User_Detail.objects.get(id=user_id)
      equipment=Equipment.objects.filter(user_id=user_id)
      
      # Total income (all time)
      total_income = Equipment.objects.filter(user_id=user_id).aggregate(Sum('totalEarning'))['totalEarning__sum'] or 0
      
      # This month's income
      from datetime import date
      today = date.today()
      first_day_of_month = today.replace(day=1)
      
      # Get accepted orders from this month
      this_month_income = Orders.objects.filter(
          owner_id=user_id,
          status='accepted',
          payment_date__gte=first_day_of_month,
          payment_date__lte=today
      ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
      
      # Count of orders this month
      this_month_orders = Orders.objects.filter(
          owner_id=user_id,
          status='accepted',
          payment_date__gte=first_day_of_month,
          payment_date__lte=today
      ).count()
      
      obj={
          'data':data,
          'equipment':equipment,
          'total_income':total_income,
          'this_month_income': this_month_income,
          'this_month_orders': this_month_orders
      }
      return render(req,'YourPerformerce.html',{'obj':obj})
    

def AddEquipment(req):
    if req.method == 'POST':
           form=EquipmentForm(req.POST,req.FILES)
           user_id=req.session.get('user_id',-1)
           if form.is_valid():
               equipment = form.save(commit=False)
               if user_id==-1:   
                 return HttpResponse("logout zaly")
               else:
                   equipment.user_id=user_id
                   equipment.save()
               return redirect('/My-equipment')
           else:
               return HttpResponse({form.errors})
    else:
        form = EquipmentForm()
        user_id=req.session.get('user_id',-1)
        obj={
          'form':form
      }
    return render(req, 'add-equipment.html', {'obj': obj})

def Equipmentpage(req):
    user_id = req.session.get('user_id', -1)
    eq = Equipment.objects.exclude(user_id=user_id)
    cs = Categories.objects.all()
    obj = {
        'categories': cs,
        'equipment': eq,
        'equipment_list': eq,
        'user_id': user_id
    }
    return render(req, 'Equipment.html', {'obj': obj})

def logout_view(request):
    request.session.flush()   
    return redirect('/')


def MyEquipment(req):
    user_id=req.session.get('user_id',-1)
    if user_id==-1 :
        return redirect('/login')
    else:
        data=Equipment.objects.filter(user_id=user_id)
        user_id=req.session.get('user_id',-1)
        obj={
            'user_id':user_id,
            'data':data
        }
        return render(req,'my_Equipment.html',{'obj':obj})

def delete_my_equipment(req,id):
    user_id=req.session.get('user_id',-1)
    if user_id==-1 :
        return redirect('/login')
    else:
      eq=Equipment.objects.get(id=id)
      eq.delete()
      return redirect('/your-performerce')
    

def view_more(req,id):
    data=Equipment.objects.get(id=id)
    user_id=req.session.get('user_id',-1)
    try:
        owner = User_Detail.objects.get(id=data.user_id)
    except User_Detail.DoesNotExist:
        owner = None

    obj={
        'equipment':data,
        'user_id':user_id,
        'owner':owner
    }
    return render(req,'view_detail.html',{'obj':obj})


def edit_my_equipment(req, id):
    equi = Equipment.objects.get(id=id)
    
    if req.method == "POST":
        form = EquipmentForm(req.POST, req.FILES, instance=equi)
        if form.is_valid():
            form.save()
            return redirect('/your-performerce') 
    else:
        form = EquipmentForm(instance=equi)
        obj = {
            'form': form,
            'equipment': equi
        }
    return render(req, 'edit-myequipment.html', {'obj':obj})


def rent_now(req, id):
    user_id = req.session.get('user_id', -1)
    
    if user_id == -1:
        return redirect('/login')
    
    try:
        equipment = Equipment.objects.get(id=id)
        owner = User_Detail.objects.get(id=equipment.user_id)
    except Equipment.DoesNotExist:
        return HttpResponse("Equipment not found", status=404)
    except User_Detail.DoesNotExist:
        owner = None
    
    customer = User_Detail.objects.get(id=user_id)
    
    if req.method == 'POST':
        form = RentalRequestForm(req.POST)
        if form.is_valid():
            # Check availability
            check_in = form.cleaned_data['Check_in']
            check_out = form.cleaned_data['Check_out']
            
            # Check if dates are valid
            if check_in >= check_out:
                return render(req, 'rent_now.html', {
                    'form': form,
                    'equipment': equipment,
                    'owner': owner,
                    'customer': customer,
                    'error': 'Check-out date must be after Check-in date'
                })
            
            # Check availability for these dates
            conflicting_orders = Orders.objects.filter(
                product_id=id,
                status__in=['accepted', 'payment_pending'],
                Check_in__lt=check_out,
                Check_out__gt=check_in
            )
            
            if conflicting_orders.exists():
                return render(req, 'rent_now.html', {
                    'form': form,
                    'equipment': equipment,
                    'owner': owner,
                    'customer': customer,
                    'error': 'Equipment not available for selected dates'
                })
            
            # Create rental request
            order = form.save(commit=False)
            order.owner_id = equipment.user_id
            order.customer_id = user_id
            order.product_id = id
            order.rent = equipment.rent
            order.owner_address = owner.mobile if owner else 'N/A'
            order.status = 'pending'
            order.total_amount = order.calculate_total()
            order.save()
            
            return redirect('/customer-orders')
    else:
        form = RentalRequestForm()
    
    obj = {
        'form': form,
        'equipment': equipment,
        'owner': owner,
        'customer': customer,
        'user_id': user_id
    }
    return render(req, 'rent_now.html', {'obj': obj})


def owner_requests(req):
    """Show all rental requests for the owner's equipment"""
    user_id = req.session.get('user_id', -1)
    
    if user_id == -1:
        return redirect('/login')
    
    # Get all rental requests for this owner's equipment
    requests = Orders.objects.filter(owner_id=user_id).order_by('-requested_at')
    
    # Get equipment names for context
    for request in requests:
        try:
            request.equipment = Equipment.objects.get(id=request.product_id)
            request.customer = User_Detail.objects.get(id=request.customer_id)
        except:
            pass
    
    pending = requests.filter(status='pending').count()
    accepted = requests.filter(status='accepted').count()
    rejected = requests.filter(status='rejected').count()
    
    obj = {
        'requests': requests,
        'pending': pending,
        'accepted': accepted,
        'rejected': rejected,
        'user_id': user_id
    }
    
    return render(req, 'owner_requests.html', {'obj': obj})


def approve_request(req, order_id):
    """Owner approves a rental request"""
    user_id = req.session.get('user_id', -1)
    
    if user_id == -1:
        return redirect('/login')
    
    try:
        order = Orders.objects.get(id=order_id, owner_id=user_id)
        order.status = 'payment_pending'
        order.response_date = timezone.now()
        order.save()
        
        return redirect('owner_requests')
    except Orders.DoesNotExist:
        return HttpResponse("Order not found", status=404)


def reject_request(req, order_id):
    """Owner rejects a rental request"""
    user_id = req.session.get('user_id', -1)
    
    if user_id == -1:
        return redirect('/login')
    
    try:
        order = Orders.objects.get(id=order_id, owner_id=user_id)
        
        if req.method == 'POST':
            remarks = req.POST.get('remarks', '')
            order.status = 'rejected'
            order.response_date = timezone.now()
            order.owner_remarks = remarks
            order.save()
            
            return redirect('owner_requests')
        else:
            obj = {
                'order': order,
                'user_id': user_id
            }
            return render(req, 'reject_request.html', {'obj': obj})
    except Orders.DoesNotExist:
        return HttpResponse("Order not found", status=404)


def process_payment(req, order_id):
    """Customer processes payment after owner approval"""
    user_id = req.session.get('user_id', -1)
    
    if user_id == -1:
        return redirect('/login')
    
    try:
        order = Orders.objects.get(id=order_id, customer_id=user_id, status='payment_pending')
        equipment = Equipment.objects.get(id=order.product_id)
        owner = User_Detail.objects.get(id=order.owner_id)
    except (Orders.DoesNotExist, Equipment.DoesNotExist, User_Detail.DoesNotExist):
        return HttpResponse("Order not found", status=404)
    
    if req.method == 'POST':
        form = PaymentForm(req.POST)
        if form.is_valid():
            order.payment_mode = form.cleaned_data['payment_mode']
            order.status = 'accepted'
            order.save()
            
            equipment.totalEarning += order.total_amount
            equipment.status = 'Rented'
            equipment.save()
            
            return redirect('payment_success', order_id=order.id)
    else:
        form = PaymentForm()
    
    obj = {
        'form': form,
        'order': order,
        'equipment': equipment,
        'owner': owner,
        'user_id': user_id
    }
    
    return render(req, 'payment.html', {'obj': obj})


def payment_success(req, order_id):
    """Show payment success page"""
    user_id = req.session.get('user_id', -1)
    
    if user_id == -1:
        return redirect('/login')
    
    try:
        order = Orders.objects.get(id=order_id)
        equipment = Equipment.objects.get(id=order.product_id)
        owner = User_Detail.objects.get(id=order.owner_id)
    except:
        return HttpResponse("Order not found", status=404)
    
    obj = {
        'order': order,
        'equipment': equipment,
        'owner': owner,
        'user_id': user_id
    }
    
    return render(req, 'payment_success.html', {'obj': obj})


def cancel_order(req, order_id):
    """Cancel a customer's order"""
    user_id = req.session.get('user_id', -1)
    
    if user_id == -1:
        return redirect('/login')
    
    try:
        order = Orders.objects.get(id=order_id, customer_id=user_id)
        
        if order.status in ['pending', 'payment_pending']:
            order.status = 'canceled'
            order.save()
            
            try:
                equipment = Equipment.objects.get(id=order.product_id)
                if equipment.status == 'Rented':
                    equipment.status = 'Available'
                    equipment.save()
            except Equipment.DoesNotExist:
                pass
            
            return redirect('customer_orders')
        else:
            return redirect('customer_orders')
    except Orders.DoesNotExist:
        return redirect('customer_orders')


def customer_orders(req):
    """Show all rental orders for the customer"""
    user_id = req.session.get('user_id', -1)
    
    if user_id == -1:
        return redirect('/login')
    
    orders = Orders.objects.filter(customer_id=user_id).order_by('-requested_at')
    
    for order in orders:
        try:
            order.equipment = Equipment.objects.get(id=order.product_id)
            order.owner = User_Detail.objects.get(id=order.owner_id)
        except:
            pass
    
    # Calculate counts for different statuses
    pending = orders.filter(status='pending').count()
    payment_pending = orders.filter(status='payment_pending').count()
    accepted = orders.filter(status='accepted').count()
    rejected = orders.filter(status='rejected').count()
    canceled = orders.filter(status='canceled').count()
    
    obj = {
        'orders': orders,
        'pending': pending,
        'payment_pending': payment_pending,
        'accepted': accepted,
        'rejected': rejected,
        'canceled': canceled,
        'user_id': user_id
    }
    
    return render(req, 'customer_orders.html', {'obj': obj})