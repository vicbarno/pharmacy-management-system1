from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.forms import  UserCreationForm
from .decorators import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import DecimalField, ExpressionWrapper, F, Q, Sum
from django.utils import timezone
from uuid import uuid4

from django.http import HttpResponseRedirect
from .forms import *
from .models import *


@login_required
def pharmacistHome(request):
    patients_total=Patients.objects.all().count()
    exipred=Stock.objects.annotate(
    expired=ExpressionWrapper(Q(valid_to__lt=Now()), output_field=BooleanField())
    ).filter(expired=True).count()
 
    out_of_stock=Stock.objects.filter(quantity__lte=0).count()
    total_stock=Stock.objects.all().count()
    low_stock = Stock.objects.filter(quantity__lte=F('reorder_level')).order_by('quantity', 'drug_name')[:8]
    low_stock_total = Stock.objects.filter(quantity__lte=F('reorder_level')).count()
    recent_sales = Dispense.objects.select_related('drug_id', 'patient_id').order_by('-dispense_at')[:6]
    sales_today = Dispense.objects.filter(dispense_at__date=timezone.localdate()).count()
    revenue_today = Dispense.objects.filter(
        dispense_at__date=timezone.localdate()
    ).aggregate(total=Sum('total_price'))['total'] or 0
    daily_cost = Dispense.objects.filter(
        dispense_at__date=timezone.localdate()
    ).aggregate(total=Sum(ExpressionWrapper(
        F('dispense_quantity') * F('drug_id__buying_price'),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )))['total'] or 0
    stock_value = Stock.objects.aggregate(total=Sum(ExpressionWrapper(
        F('quantity') * F('buying_price'),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )))['total'] or 0

    context={
"patients_total":patients_total,
        "expired_total":exipred,
        "out_of_stock":out_of_stock,
        "total_drugs":total_stock,
        "low_stock":low_stock,
        "low_stock_total":low_stock_total,
        "recent_sales":recent_sales,
        "sales_today":sales_today,
        "revenue_today":revenue_today,
        "daily_net_profit":revenue_today - daily_cost,
        "stock_value":stock_value,
        
    }
    return render(request,'pharmacist_templates/pharmacist_home.html',context)

@login_required
def userProfile(request):
    staff=Pharmacist.objects.all()
    form=CustomerForm()
    if request.method == "POST":
       

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        address = request.POST.get('address')

      
        customuser = CustomUser.objects.get(id=request.user.id)
        customuser.first_name = first_name
        customuser.last_name = last_name
        
        customuser.save()
        staff = Pharmacist.objects.get(admin=customuser.id)
        form=CustomerForm(request.POST,request.FILES,instance=staff)

        staff.address = address
        if form.is_valid():
            form.save()
        staff.save()
        
        messages.success(request, "Profile Updated Successfully")
        return redirect('pharmacist_profile')

    context={
        "staff":staff,
        "form":form
    }
      

    return render(request,'pharmacist_templates/staff_profile.html',context)

def managePatientsPharmacist(request):
   
    patient=Patients.objects.all()
    context={
        "patients":patient
    }
    return render(request,'pharmacist_templates/manage_patients.html',context)


def managePrescription(request):
    precrip=Dispense.objects.all()

    context={
        "prescrips":precrip,
    }
    return render(request,'pharmacist_templates/patient_prescrip.html',context)


@login_required
def pointOfSale(request):
    search = request.GET.get('q', '').strip()
    form = PointOfSaleForm(request.POST or None, search=search)
    stock_results = Stock.objects.filter(quantity__gt=0).order_by('drug_name')
    if search:
        stock_results = stock_results.filter(
            Q(drug_name__icontains=search)
            | Q(item_id__icontains=search)
            | Q(supplier__icontains=search)
        )
    else:
        stock_results = stock_results[:50]
    recent_sales = Dispense.objects.select_related('drug_id', 'patient_id').order_by('-dispense_at')[:20]
    stock_catalog = [
        {
            'id': item['id'],
            'name': item['drug_name'],
            'quantity': item['quantity'],
            'price': str(item['selling_price']),
        }
        for item in Stock.objects.filter(quantity__gt=0).values(
            'id', 'drug_name', 'quantity', 'selling_price'
        )
    ]

    if request.method == 'POST' and form.is_valid():
        stock_id = form.cleaned_data['drug_id'].pk
        quantity = form.cleaned_data['dispense_quantity']

        with transaction.atomic():
            stock = Stock.objects.select_for_update().get(pk=stock_id)
            if stock.valid_to and stock.valid_to < timezone.now():
                form.add_error('drug_id', 'This medicine has expired and cannot be sold.')
            elif stock.quantity < quantity:
                form.add_error('dispense_quantity', f'Only {stock.quantity} unit(s) are available.')
            else:
                total_price = stock.selling_price * quantity
                Stock.objects.filter(pk=stock.pk).update(quantity=stock.quantity - quantity)
                Dispense.objects.create(
                    drug_id=stock,
                    patient_id=form.cleaned_data['patient_id'],
                    dispense_quantity=quantity,
                    taken=form.cleaned_data['taken'],
                    instructions=form.cleaned_data['instructions'] or '',
                    unit_price=stock.selling_price,
                    total_price=total_price,
                    payment_method=form.cleaned_data['payment_method'],
                    receipt_no=f'POS-{uuid4().hex[:10].upper()}',
                )

                messages.success(
                    request,
                    f'{quantity} x {stock.drug_name} sold successfully. Total: KES {total_price:,.2f}',
                )
                return redirect('point_of_sale')

    context = {
        'form': form,
        'recent_sales': recent_sales,
        'stock_results': stock_results,
        'stock_search': search,
        'stock_catalog': stock_catalog,
    }
    return render(request, 'pharmacist_templates/point_of_sale.html', context)


    
def manageStock(request):
    search = request.GET.get('q', '').strip()
    status = request.GET.get('status', 'all')
    stocks = Stock.objects.select_related('category').all()
    if search:
        stocks = stocks.filter(Q(drug_name__icontains=search) | Q(item_id__icontains=search) | Q(supplier__icontains=search))
    if status == 'low':
        stocks = stocks.filter(quantity__lte=F('reorder_level'))
    elif status == 'out':
        stocks = stocks.filter(quantity__lte=0)
    elif status == 'available':
        stocks = stocks.filter(quantity__gt=0)
    stocks = stocks.order_by('drug_name')
    ex=Stock.objects.annotate(
    expired=ExpressionWrapper(Q(valid_to__lt=Now()), output_field=BooleanField())
    ).filter(expired=True)
    eo=Stock.objects.annotate(
    expired=ExpressionWrapper(Q(valid_to__lt=Now()), output_field=BooleanField())
    ).filter(expired=False)
    context = {
        "stocks": stocks,
                "expired":ex,

    }
    return render(request,'pharmacist_templates/manage_stock.html',context)


def manageDispense(request,pk):
    queryset=Patients.objects.get(id=pk)
    prescrips=queryset.prescription_set.all()
    
    print(prescrips)
    form=DispenseForm(request.POST or None,initial={'patient_id':queryset} )
    drugs=Stock.objects.all()
    ex=Stock.objects.annotate(
    expired=ExpressionWrapper(Q(valid_to__lt=Now()), output_field=BooleanField())
    ).filter(expired=True)
    eo=Stock.objects.annotate(
    expired=ExpressionWrapper(Q(valid_to__lt=Now()), output_field=BooleanField())
    ).filter(expired=False)
    # print(ex)
      
   
    try:  
        
        if request.method == 'POST':
            if form.is_valid(): 
                username = form.cleaned_data['taken']
                qu=form.cleaned_data['dispense_quantity']
                ka=form.cleaned_data['drug_id']
                # print(username)
            
            
                    
                stock= eo=Stock.objects.annotate(
                expired=ExpressionWrapper(Q(valid_to__lt=Now()), output_field=BooleanField())
                ).filter(expired=False).get(id=username)
                form=DispenseForm(request.POST or None, instance=stock)
                instance=form.save()
                # print(instance)
                instance.quantity-=qu
                instance.save()

                form=DispenseForm(request.POST or None ,initial={'patient_id':queryset})
                form.save()

                messages.success(request, "Drug Has been Successfully Dispensed")

                return redirect('manage_patient_pharmacist')
            else:
                messages.error(request, "Validty Error")

                return redirect('manage_patient_pharmacist')

        context={
            "patients":queryset,
            "form":form,
            # "stocks":stock,
            "drugs":drugs,
            "prescrips":prescrips,
"expired":ex,
"expa":eo,

            }
        if request.method == 'POST':
        
            print(drugs)
            context={
                "drugs":drugs,
                form:form,
                "prescrips":prescrips,
                "patients":queryset,
                "expired":ex,
                "expa":eo,

            }
    except:
        messages.error(request, "Dispensing Not Allowed! The Drug is Expired ,please contanct the admin for re-stock ")
        return redirect('manage_patient_pharmacist')
    context={
            "patients":queryset,
            "form":form,
            # "stocks":stock,
            "drugs":drugs,
            "prescrips":prescrips,
"expired":ex,
"expa":eo,

            }
    
    return render(request,'pharmacist_templates/manage_dispense.html',context)



def patient_feedback_message(request):
    feedbacks = PatientFeedback.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'pharmacist_templates/patient_feedback.html', context)

@csrf_exempt
def patient_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')
    try:
        feedback =  PatientFeedback.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")

def deletefeedback(request,pk):
    try:
        fed=PatientFeedback.objects.get(id=pk)
        if request.method == 'POST':
            fed.delete()
            messages.success(request, "Feedback  deleted successfully")
            return redirect('patient_feedback_message')

    except:
        messages.error(request, "Feedback Error, Please Check again")
        return redirect('patient_feedback_message')


   
    return render(request,'pharmacist_templates/sure_delete.html')
    



def drugDetails(request,pk):
    stocks=Stock.objects.get(id=pk)
    context={
        "stocks":stocks,
       

    }
    return render(request,'pharmacist_templates/view_drug.html',context)



def deleteDispense4(request,pk):
    try:
        fed=Dispense.objects.get(id=pk)
        if request.method == 'POST':
            fed.delete()
            messages.success(request, "Dispense  deleted successfully")
            return redirect('pharmacist_prescription')

    except:
        messages.error(request, "Delete Error, Please Check again")
        return redirect('pharmacist_prescription')


   
    return render(request,'pharmacist_templates/sure_delete.html')
    








































































# # def dispenseDrug(request,pk):
# #     queryset=Patients.objects.get(id=pk)
# #     form=DispenseForm(initial={'patient_id':queryset})
# #     if request.method == 'POST':
# #         form=DispenseForm(request.POST or None)
# #         if form.is_valid():
# #             form.save()
            
    
# #     context={
# #         # "title":' Issue' + str(queryset.item_name),
# #         "queryset":queryset,
# #         "form":form,
# #         # "username":" Issue By" + str(request.user),
# #     }
# #     return render(request,"pharmacist_templates/dispense_drug.html",context)

# # def manageDispense(request):
# #     disp=De.objects.all()
# #     context={
# #         "prescrips":disp,
# #     }
# #     return render(request,'pharmacist_templates/manage_dispense.html',context)




# def dispense(request,pk):
#     queryset=Stock.objects.get(id=pk)
#     form=DispenseForm2(request.POST or None,instance=queryset)
#     if form.is_valid():
#         instance=form.save(commit=False)
#         instance.quantity-=instance.dispense_quantity
#         print(instance.drug_id.quantity)
#         print(instance.dispense_quantity)
#         instance.save()

#         return redirect('pharmacist_disp')

       
    
#     context={
#         "queryset":queryset,
#         "form":form,
#     }
#     return render(request,'pharmacist_templates/dispense_form.html',context)

