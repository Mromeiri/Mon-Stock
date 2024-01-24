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
from django.db.models import F, ExpressionWrapper, fields
from django.db.models import Subquery  
from decimal import Decimal
from datetime import date, timedelta
    
dicc=55
dicmodel={}
dicmodel['Groupes'] = '50'
dicmodel["Utilisateurs"] = "5"







def indexx(request):
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

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
    yearly_totals_2023 = get_total_amount_by_year(timezone.now().year)
    yearly_totals_center1 = get_total_amount_by_year(timezone.now().year, center=1)
    yearly_totals_center2 = get_total_amount_by_year(timezone.now().year, center=2)
    yearly_totals_center3 = get_total_amount_by_year(timezone.now().year, center=3)
    # Top Client
    top_clients = Sale.objects.values(
    'client__id', 'client__name', 'client__address', 'client__phone',
    ).annotate(
        total_amount=Sum(ExpressionWrapper(F('quantity_sold') * F('unit_price'), output_field=fields.DecimalField()))
    ).order_by('-total_amount')[:5]
    top_product = Sale.objects.values(
    'product__designation', 'product__Type', 'product__quantity_in_stock', 'product__image'
    ).annotate(
        total=Sum(ExpressionWrapper(F('quantity_sold')* F('unit_price') , output_field=fields.DecimalField())),
        quantity_sold=Sum(ExpressionWrapper(F('quantity_sold') , output_field=fields.DecimalField()))
    ).order_by('-quantity_sold')[:5]
    
    # # Print or use the top clients
    # print(top_client_instances)
    
    # Create a dictionary with 'total_amount' as a key-value pair
    context = {
                'months':months,
                'total_sales': full,
               'products':products,
               'notification':notification,
               'top_4_suppliers':result,
               'total_commande':yearly_total,
               'new_clients_count':new_clients_count,
               'new_clients_percentage':new_clients_percentage,
                'yearly_totals_2023':yearly_totals_2023,
                'yearly_totals_center1':yearly_totals_center1,
                'yearly_totals_center2':yearly_totals_center2,
                'yearly_totals_center3':yearly_totals_center3,
                'top_clients':top_clients,
                'top_product':top_product,
                'get_total_achat_by_year':get_total_achat_by_year(timezone.now().year),
              
              }
    
    return {'app_view1': context}

def get_total_amount_by_year(year, center=None):
    monthly_totals = {}
    for month in range(1, 13):
        # Calculate start and end dates of each month in the specified year
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, monthrange(year, month)[1])

        # Query to calculate total amount for each month
        filter_params = {'sale_date__gte': start_date, 'sale_date__lte': end_date}
       
        filter_params['center_id'] = center
        


        total_amount = Sale.objects.filter(**filter_params).aggregate(total=Sum(F('unit_price') * F('quantity_sold')))

        # Store total amount for the month as a float
        monthly_totals[start_date.strftime('%b').lower()] = float(total_amount['total'] or 0) if total_amount['total'] is not None else 0

    return monthly_totals
def get_total_achat_by_year(year):
    monthly_totals = {}
    for month in range(1, 13):
        # Calculate start and end dates of each month in the specified year
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, monthrange(year, month)[1])

        # Query to calculate total amount for each month
        filter_params = {'date_created__gte': start_date, 'date_created__lte': end_date}
       
       
        


        total_achat = Commande.objects.filter(**filter_params).aggregate(total=Sum(F('unit_price') * F('quantity')))

        # Store total amount for the month as a float
        monthly_totals[start_date.strftime('%b').lower()] = float(total_achat['total'] or 0) if total_achat['total'] is not None else 0

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
def get_top_client_of_each_month(year):
    top_clients_of_each_month = []

    # Itérez sur chaque mois de l'année
    for month in range(1, 13):
        # Obtenez la date de début et de fin du mois
        first_day_of_month = datetime(year, month, 1)
        last_day_of_month = first_day_of_month.replace(
            day=monthrange(year, month)[1])

        # Obtenez le top client du mois en fonction de la quantité totale de produits vendus
        top_client = Sale.objects.filter(
            sale_date__gte=first_day_of_month,
            sale_date__lte=last_day_of_month
        ).values('client__name', 'client__address', 'client__phone',).annotate(total_quantity=Sum(F('unit_price') * F('quantity_sold'))).order_by('-total_quantity').first()

        # Ajoutez le résultat à la liste
        top_clients_of_each_month.append({
            'month': month,
            'top_client': top_client
        })

    return top_clients_of_each_month
