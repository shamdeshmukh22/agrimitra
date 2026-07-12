from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import Sign_up,Login,EquipmentForm,RentalRequestForm,PaymentForm,RentalAdjustmentForm
from .models import User_Detail,Categories,Equipment,Orders,RentalAdjustment
from django.db.models import Sum
from django.core.paginator import Paginator
from datetime import date, datetime
from django.utils import timezone
import math
import json

def HomePage(req):
    user_id=req.session.get('user_id',-1)
    update_equipment_status()
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
    user_id = req.session.get('user_id', -1)
    if req.method == 'POST':

        form = Sign_up(req.POST)
        if form.is_valid():
            form.save()
            return redirect('/login')
            
    else:
        form = Sign_up()
    obj = {
        'user_id': user_id,
        'form': form
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
      
      total_income = Equipment.objects.filter(user_id=user_id).aggregate(Sum('totalEarning'))['totalEarning__sum'] or 0
      
      from datetime import date
      today = date.today()
      first_day_of_month = today.replace(day=1)
      
      this_month_income = Orders.objects.filter(
          owner_id=user_id,
          status='accepted',
          payment_date__gte=first_day_of_month,
          payment_date__lte=today
      ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
      
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
    eq = Equipment.objects.exclude(user_id=user_id).order_by('-id')
    
    paginator = Paginator(eq, 6)
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cs = Categories.objects.all()
    obj = {
        'categories': cs,
        'equipment': page_obj,
        'equipment_list': eq,
        'user_id': user_id,
        'page_obj': page_obj
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
   
def view_more(req, id):
    user_id = req.session.get('user_id', -1)
    if user_id == -1:
        return redirect('/login')

    data = Equipment.objects.get(id=id)
    orders = Orders.objects.filter(product_id=id, status__in=["accepted", "payment_pending"])
    
    booked_dates = []
    for order in orders:
        booked_dates.append({
            'check_in': order.Check_in.strftime('%Y-%m-%d'),
            'check_out': order.Check_out.strftime('%Y-%m-%d'),
            'total_amount': order.total_amount
        })

    try:
        owner = User_Detail.objects.get(id=data.user_id)
        user=User_Detail.objects.get(id=user_id)
        lat2=owner.latitude
        lon2=owner.longitude
        lat1=user.latitude
        lon1=user.longitude

        R=6371
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2)**2 +            math.cos(phi1) * math.cos(phi2) *            math.sin(delta_lambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        final_distance = round(distance, 2)

    except User_Detail.DoesNotExist:
        owner = None
        user=None

    obj = {
        'equipment': data,
        'user_id': user_id,
        'owner': owner,
        'user': user,
        'distance': final_distance,
        'booked_dates': json.dumps(booked_dates)
    }
    return render(req, 'view_detail.html', {'obj': obj})

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
            
            check_in = form.cleaned_data['Check_in']
            check_out = form.cleaned_data['Check_out']
            
            if check_in >= check_out:
                return render(req, 'rent_now.html', {
                    'form': form,
                    'equipment': equipment,
                    'owner': owner,
                    'customer': customer,
                    'error': 'Check-out date must be after Check-in date'
                })
            
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
    
    requests = Orders.objects.filter(owner_id=user_id).order_by('-requested_at')
    
    for request in requests:
        try:
            request.equipment = Equipment.objects.get(id=request.product_id)
            request.customer = User_Detail.objects.get(id=request.customer_id)
        except:
            pass
    
    adj_requests = RentalAdjustment.objects.filter(
        order__in=Orders.objects.filter(owner_id=user_id),
        status='pending'
    ).select_related('order')
    
    for adj in adj_requests:
        try:
            adj.order.equipment = Equipment.objects.get(id=adj.order.product_id)
            adj.order.customer = User_Detail.objects.get(id=adj.order.customer_id)
            adj.refund_amount = abs(adj.extra_amount)
        except:
            pass

    pending = requests.filter(status='pending').count()
    accepted = requests.filter(status='accepted').count()
    rejected = requests.filter(status='rejected').count()
    
    obj = {
        'requests': requests,
        'adj_requests': adj_requests,
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
            order.pending_adj = order.adjustments.filter(status='pending').first()
            order.approved_ext_adj = order.adjustments.filter(status='approved', adjustment_type='extend').first()
        except:
            pass
    
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

def update_equipment_status():
    file_path = "last_run.txt"
    today = str(date.today())

    try:
        with open(file_path, "r") as f:
            if f.read().strip() == today:
                return
    except FileNotFoundError:
        pass

    today_date = date.today()

    expired_orders = Orders.objects.filter(status='accepted', Check_out__lt=today_date)
    
    if expired_orders.exists():
        
        product_ids = list(expired_orders.values_list('product_id', flat=True))
        
        Equipment.objects.filter(id__in=product_ids).update(status='Available')
        
        expired_orders.update(status='completed')

    with open(file_path, "w") as f:
        f.write(today)

def request_extend_days(req, order_id):
    """Customer requests to extend rental by choosing a new (later) checkout date."""
    user_id = req.session.get('user_id', -1)
    if user_id == -1:
        return redirect('/login')

    try:
        order = Orders.objects.get(id=order_id, customer_id=user_id, status='accepted')
        equipment = Equipment.objects.get(id=order.product_id)
    except (Orders.DoesNotExist, Equipment.DoesNotExist):
        return HttpResponse('Order not found or not eligible.', status=404)

    if order.adjustments.filter(status='pending').exists():
        return redirect('customer_orders')

    error = None
    if req.method == 'POST':
        form = RentalAdjustmentForm(req.POST)
        if form.is_valid():
            new_date = form.cleaned_data['new_checkout_date']
            if new_date <= order.Check_out:
                error = 'New date must be AFTER current check-out date.'
            else:
                
                conflicts = Orders.objects.filter(
                    product_id=order.product_id,
                    status__in=['accepted', 'payment_pending'],
                    Check_in__lt=new_date,
                    Check_out__gt=order.Check_out
                ).exclude(id=order.id)
                if conflicts.exists():
                    error = 'Equipment is already booked for some of those extra days.'
                else:
                    adj = RentalAdjustment(
                        order=order,
                        adjustment_type='extend',
                        new_checkout_date=new_date,
                        customer_note=form.cleaned_data.get('customer_note', '')
                    )
                    adj.calculate_extra()
                    adj.save()
                    order.status = 'extend_requested'
                    order.save()
                    return redirect('customer_orders')
    else:
        form = RentalAdjustmentForm()

    obj = {
        'form': form,
        'order': order,
        'equipment': equipment,
        'error': error,
        'user_id': user_id,
    }
    return render(req, 'extend_days.html', {'obj': obj})

def request_early_return(req, order_id):
    """Customer requests early return — requests new (earlier) checkout date."""
    user_id = req.session.get('user_id', -1)
    if user_id == -1:
        return redirect('/login')

    try:
        order = Orders.objects.get(id=order_id, customer_id=user_id, status='accepted')
        equipment = Equipment.objects.get(id=order.product_id)
    except (Orders.DoesNotExist, Equipment.DoesNotExist):
        return HttpResponse('Order not found or not eligible.', status=404)

    if order.adjustments.filter(status='pending').exists():
        return redirect('customer_orders')

    error = None
    if req.method == 'POST':
        form = RentalAdjustmentForm(req.POST)
        if form.is_valid():
            new_date = form.cleaned_data['new_checkout_date']
            today = date.today()
            if new_date >= order.Check_out:
                error = 'New date must be BEFORE current check-out date for early return.'
            elif new_date < today:
                error = 'New return date cannot be in the past.'
            else:
                adj = RentalAdjustment(
                    order=order,
                    adjustment_type='reduce',
                    new_checkout_date=new_date,
                    customer_note=form.cleaned_data.get('customer_note', '')
                )
                adj.calculate_extra()
                adj.save()
                order.status = 'reduce_requested'
                order.save()
                return redirect('customer_orders')
    else:
        form = RentalAdjustmentForm()

    obj = {
        'form': form,
        'order': order,
        'equipment': equipment,
        'error': error,
        'user_id': user_id,
    }
    return render(req, 'early_return.html', {'obj': obj})

def owner_approve_extend(req, adj_id):
    """Owner approves an extend-days request → customer can now pay extra."""
    user_id = req.session.get('user_id', -1)
    if user_id == -1:
        return redirect('/login')

    try:
        adj = RentalAdjustment.objects.get(id=adj_id, adjustment_type='extend', status='pending')
        order = Orders.objects.get(id=adj.order_id, owner_id=user_id)
    except (RentalAdjustment.DoesNotExist, Orders.DoesNotExist):
        return HttpResponse('Request not found.', status=404)

    adj.status = 'approved'
    adj.responded_at = timezone.now()
    adj.save()
    
    order.status = 'accepted'
    order.save()
    return redirect('owner_requests')

def owner_approve_reduce(req, adj_id):
    """Owner confirms early return — refunds remaining days, marks equipment Available."""
    user_id = req.session.get('user_id', -1)
    if user_id == -1:
        return redirect('/login')

    try:
        adj = RentalAdjustment.objects.get(id=adj_id, adjustment_type='reduce', status='pending')
        order = Orders.objects.get(id=adj.order_id, owner_id=user_id)
        equipment = Equipment.objects.get(id=order.product_id)
    except (RentalAdjustment.DoesNotExist, Orders.DoesNotExist, Equipment.DoesNotExist):
        return HttpResponse('Request not found.', status=404)

    refund_amount = abs(adj.extra_amount)

    order.Check_out = adj.new_checkout_date
    order.total_amount = order.total_amount - refund_amount
    order.status = 'completed'
    order.save()

    equipment.status = 'Available'
    equipment.totalEarning = max(0, equipment.totalEarning - refund_amount)
    equipment.save()

    adj.status = 'completed'
    adj.responded_at = timezone.now()
    adj.save()

    return redirect('owner_requests')

def owner_reject_adjustment(req, adj_id):
    """Owner rejects any adjustment request (extend or reduce)."""
    user_id = req.session.get('user_id', -1)
    if user_id == -1:
        return redirect('/login')

    try:
        adj = RentalAdjustment.objects.get(id=adj_id, status='pending')
        order = Orders.objects.get(id=adj.order_id, owner_id=user_id)
    except (RentalAdjustment.DoesNotExist, Orders.DoesNotExist):
        return HttpResponse('Request not found.', status=404)

    remarks = req.POST.get('remarks', '') if req.method == 'POST' else ''
    adj.status = 'rejected'
    adj.owner_remarks = remarks
    adj.responded_at = timezone.now()
    adj.save()

    order.status = 'accepted'
    order.save()

    return redirect('owner_requests')

def pay_extra_days(req, adj_id):
    """Customer pays for approved extension."""
    user_id = req.session.get('user_id', -1)
    if user_id == -1:
        return redirect('/login')

    try:
        adj = RentalAdjustment.objects.get(id=adj_id, adjustment_type='extend', status='approved')
        order = Orders.objects.get(id=adj.order_id, customer_id=user_id)
        equipment = Equipment.objects.get(id=order.product_id)
        owner = User_Detail.objects.get(id=order.owner_id)
    except Exception:
        return HttpResponse('Request not found.', status=404)

    if req.method == 'POST':
        form = PaymentForm(req.POST)
        if form.is_valid():
            
            order.Check_out = adj.new_checkout_date
            order.total_amount += adj.extra_amount
            order.payment_mode = form.cleaned_data['payment_mode']
            order.status = 'accepted'
            order.save()

            equipment.totalEarning += adj.extra_amount
            equipment.save()

            adj.status = 'paid'
            adj.save()

            return redirect('adjustment_success', adj_id=adj.id)
    else:
        form = PaymentForm()

    obj = {
        'form': form,
        'adj': adj,
        'order': order,
        'equipment': equipment,
        'owner': owner,
        'user_id': user_id,
    }
    return render(req, 'pay_extra_days.html', {'obj': obj})

def adjustment_success(req, adj_id):
    """Show success page after adjustment payment or early return."""
    user_id = req.session.get('user_id', -1)
    if user_id == -1:
        return redirect('/login')

    try:
        adj = RentalAdjustment.objects.get(id=adj_id)
        order = Orders.objects.get(id=adj.order_id)
        equipment = Equipment.objects.get(id=order.product_id)
    except Exception:
        return HttpResponse('Not found.', status=404)

    obj = {
        'adj': adj,
        'order': order,
        'equipment': equipment,
        'user_id': user_id,
    }
    return render(req, 'adjustment_success.html', {'obj': obj})

