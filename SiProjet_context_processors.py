from calendar import monthrange
from datetime import datetime
from django.db.models import Count,Sum
from django.conf import settings
from django.shortcuts import render
from django.db.models.functions import Coalesce
from django.db.models import F, ExpressionWrapper, DecimalField
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth
from gestionStock.models import *

    
dicc=55
dicmodel={}
dicmodel['Groupes'] = '50'
dicmodel["Utilisateurs"] = "5"







def indexx(request):
    
    total_amount = Sale.objects.all()
    full = 0
    for total in total_amount:
        full+=total.quantity_sold * total.unit_price

    products = Product.objects.all()
    notification = Notification.objects.all()

    top_suppliers = (
        Commande.objects.values('supplier__name')
        .annotate(
            total_value=ExpressionWrapper(
                F('unit_price') * F('quantity'),
                output_field=DecimalField()
            )
        )
        .order_by('-total_value')[:4]
    )

    # Format the data for output
    result = []
    for supplier_data in top_suppliers:
        supplier_name = supplier_data['supplier__name']
        total_value = supplier_data['total_value']
        result.append({'supplier_name': supplier_name, 'total_value': abbreviate_value(total_value)})
    yearly_total = Commande.objects.filter(
            date_created__year=timezone.now().year
        ).aggregate(
            total=Sum(models.F('unit_price') * models.F('quantity'), output_field=models.FloatField())
        )['total'] or 0.0

    new_clients_count = Client.objects.filter(date_of_registration__year=timezone.now().year).count()
    total_clients_count = Client.objects.count()
    existing_clients_count = total_clients_count - new_clients_count

        # Calculate the percentages
    new_clients_percentage = (new_clients_count / total_clients_count) * 100 if total_clients_count != 0 else 0

    # Sales Graph


# Get the current year


   

    

    

    
       

    # total_assisted_rows = Assisted.objects.count()
    # total_students = Etudiant.objects.count()
    # total_amount_students = Etudiant.objects.aggregate(total_amount=models.Sum('amount'))['total_amount'] or 0
    # p = (calculate_final_amount_for_all())
    # percentage_final_amounts_all_students = (
    #     p / float(total_amount)
    # ) * 100 if total_amount != 0 else 0

    
    

  

    yearly_totals_2023 = get_total_amount_by_year(2024)
    print(yearly_totals_2023)
    result_string = str(yearly_totals_2023['dec']).replace("(", "").replace(")", "")

    jan_value = yearly_totals_2023['jan']
    feb_value = yearly_totals_2023['feb']
    mar_value = yearly_totals_2023['mar']
    apr_value = yearly_totals_2023['apr']
    may_value = yearly_totals_2023['may']
    jun_value = yearly_totals_2023['jun']
    jul_value = yearly_totals_2023['jul']
    aug_value = yearly_totals_2023['aug']
    sep_value = yearly_totals_2023['sep']
    oct_value = yearly_totals_2023['oct']
    nov_value = yearly_totals_2023['nov']
    dec_value = yearly_totals_2023['dec']
    print(jan_value)

    
    # Create a dictionary with 'total_amount' as a key-value pair
    context = {
                'total_sales': full,
               'products':products,
               'notification':notification,
               'top_4_suppliers':result,
               'total_commande':yearly_total,
               'new_clients_count':new_clients_count,
               'new_clients_percentage':new_clients_percentage,

               'jan_value': jan_value, 
               'feb_value' : yearly_totals_2023['feb'],
                'mar_value' : yearly_totals_2023['mar'],
                'apr_value' : yearly_totals_2023['apr'],
                'may_value' : yearly_totals_2023['may'],
                'jun_value' : yearly_totals_2023['jun'],
                'jul_value' : yearly_totals_2023['jul'],
                'aug_value' : yearly_totals_2023['aug'],
                'sep_value' : yearly_totals_2023['sep'],
                'oct_value' : yearly_totals_2023['oct'],
                'nov_value' : yearly_totals_2023['nov'],
                'dec_value' :yearly_totals_2023['dec'],

               
    #           'percentage_final_amounts_all_students':  percentage_final_amounts_all_students

              
              }
    
    return {'app_view1': context}


# def calculate_final_amount_for_all():
#     # Fetch all instances of your model
#     all_instances = Etudiant.objects.all()
#     total = 0.0
#     for obj in all_instances:
#         total_amount = obj.payments.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
#         assisted_cost = 0

#         # Calculate the assisted cost for the current object
#         for assisted_instance in obj.assisted_set.all():
#             if assisted_instance.matiere.prix_seance is not None:
#                 assisted_cost += assisted_instance.matiere.prix_seance / 4

#         # Calculate the final amount by subtracting assisted cost from total amount
#         final_amount = float(total_amount) - float(Decimal(assisted_cost))

#         # Assign or store the final amount in your model instance or print it
#         # For example:
#         # obj.final_amount = final_amount
#         # obj.save()
#         print(f"For {obj}: Final Amount = {final_amount}")
#         total +=final_amount

#     return float(total) 

def get_total_amount_by_year(year):
    monthly_totals = {}
    for month in range(1, 13):
        # Calculate start and end dates of each month in the specified year
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, monthrange(year, month)[1])

        # Query to calculate total amount for each month
        total_amount = Sale.objects.filter(
            sale_date__gte=start_date, sale_date__lte=end_date).aggregate(total=Sum( F('unit_price') * F('quantity_sold')))

        # Store total amount for the month as a float
        monthly_totals[start_date.strftime('%b').lower()] = float(total_amount['total'] or 0) if total_amount['total'] is not None else 0

    return monthly_totals
 


def abbreviate_value(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value

    if value > 1000000:
        return f"{value / 1000000:.1f}m"
    elif value > 1000:
        return f"{value / 1000:.1f}k"
    else:
        return str(value)