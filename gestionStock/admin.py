import os
from django.contrib import admin
from .models import *
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from gestionStock.Widgets import CustomForeignKeyRawIdFormField

from io import BytesIO
from reportlab.lib.pagesizes import letter,legal,landscape,A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle



from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle




from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph


# def generate_pdf(products):
#     buffer = BytesIO()

#     # Create a PDF document
#     pdf = SimpleDocTemplate(buffer, pagesize=letter)
#     width, height = letter

#     # Set up your logos (adjust the path as per your project structure)
#     BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     logo_path_left = BASE_DIR + '/static/img/favicon2.png'
#     logo_path_right = BASE_DIR + '/static/img/favicon2.png'  # Add your right logo path

#     logo_left = Image.open(logo_path_left)
#     logo_right = Image.open(logo_path_right)

#     # Add logos to the PDF
#     elements = []

#     # Set title
#     title_text = "La liste des produits"
#     title = Paragraph(title_text, getSampleStyleSheet()["Title"])
#     elements.append(title)
#     elements.append(Spacer(1, 50.0394))  # Adjust the second parameter to set the height in points

#     # Create table data
#     table_data = [["Designation", "Type", "Quantity"]]
#     for product in products:
#         table_data.append([product.designation, product.get_type_display, str(product.quantity_in_stock)])

#     # Define table style
#     style = TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background color
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Header text color
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Centered text for the whole table
#         ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Alternate row background color
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Table grid
#     ])

#     # Create the table
#     table = Table(table_data, style=style, colWidths=[150, 100, 100])
    
#     elements.append(table)


#     # Build the PDF with the elements
#     pdf.build(elements, onFirstPage=lambda canvas, doc: add_logo(canvas, doc, logo_left, logo_right))
#     buffer.seek(0)
#     return buffer

def generate_pdf(queryset, model_name):
    buffer = BytesIO()

    # Create a PDF document
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    # Set up your logos (adjust the path as per your project structure)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path_left = BASE_DIR + '/static/img/favicon1.png'
    logo_path_right = BASE_DIR + '/static/img/favicon1.png'  # Add your right logo path

    logo_left = Image.open(logo_path_left)
    logo_right = Image.open(logo_path_right)

    # Add logos to the PDF
    elements = []

    # Set title
    title_text = f"List of {model_name}s"
    title = Paragraph(title_text, getSampleStyleSheet()["Title"])
    elements.append(title)
    elements.append(Spacer(1, 20))  # Adjust the second parameter to set the height in points

    # Create table data dynamically based on the model's fields
    table_data = []

    # Extract field names and add them as headers
    headers = [field.name.capitalize() for field in queryset.model._meta.fields]
    table_data.append(headers)

    # Extract data for each object in the queryset
    for obj in queryset:
        row_data = [str(getattr(obj, field.name)) for field in queryset.model._meta.fields]
        table_data.append(row_data)

    # Define table style
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    # Create the table
    table = Table(table_data, style=style, colWidths=[115] * len(headers))
    elements.append(table)
    elements.append(Spacer(1, 20.0394))
    # Add date
    date_text = f"Algeria on : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    date_paragraph = Paragraph(date_text, getSampleStyleSheet()["Normal"])
    elements.append(date_paragraph)

    # Add signature
    signature_text = "Signature: Omeiri Benhocine"
    signature_style = ParagraphStyle(
        'SignatureStyle',
        parent=getSampleStyleSheet()["Normal"],
        fontName='Helvetica-Bold',  # Set your desired font
        fontSize=12,  # Set your desired font size
    )
    signature_paragraph = Paragraph(signature_text, getSampleStyleSheet()["Normal"])
    elements.append(signature_paragraph)

    # Build the PDF with the elements
    pdf.build(elements, onFirstPage=lambda canvas, doc: add_logo(canvas, doc, logo_left, logo_right))
    buffer.seek(0)
    return buffer

def add_logo(canvas, doc, logo_left, logo_right):
    # Draw logos on the PDF using the canvas
    logo_width = 50
    logo_height = 50
    canvas.drawInlineImage(logo_left, 50, doc.pagesize[1] - 100, width=logo_width, height=logo_height)
    canvas.drawInlineImage(logo_right, doc.pagesize[0] - logo_width - 50, doc.pagesize[1] - 100, width=logo_width, height=logo_height)
def imprimer_pdf(self, request, queryset):
        model_name = queryset.model._meta.verbose_name.capitalize()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{model_name}s.pdf"'

        # Call the generate_pdf function passing the selected products
        pdf = generate_pdf(queryset,model_name)

        response.write(pdf.getvalue())
        return response
imprimer_pdf.short_description = "Imprimer PDF"
admin.site.add_action(imprimer_pdf)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'designation','Type','quantity_in_stock','Avrege_quantity','image')  # Customize displayed fields
    search_fields = ('id', 'designation','Type','quantity_in_stock')
    actions = ['imprimer_pdf']

    

    

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    actions = ['imprimer_pdf']
    autocomplete_fields = ('produit',)
    readonly_fields=('payed',)
    list_display = ('get_commande_number', 'supplier', 'produit', 'quantity', 'unit_price', 'total', 'state', 'date_created','payed')
    

    def get_commande_number(self, obj):
        return obj.id
    get_commande_number.short_description = 'N° order'

    search_fields = ('supplier__name', 'produit__name')
    list_filter = ('supplier', 'state')

    def total(self, obj):
        return obj.quantity * obj.unit_price
    total.short_description = 'Total'

    # Optional: Allow ordering by the computed field 'total'
    total.admin_order_field = 'total'

@admin.register(ArriveInStock)
class ArriveInStockAdmin(admin.ModelAdmin):
    actions = ['imprimer_pdf']
    list_display = ('get_commande_number','get_commande_numbercommande','date_arrive', 'get_commande_quantity_arrive','get_quantity_transferred' ,'get_produit_name','get_supplier_name')
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "commande":
            kwargs["queryset"] = Commande.objects.exclude(state__in=['3', '4'])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    def get_commande_numbercommande(self, obj):
        return obj.commande
    get_commande_numbercommande.short_description = 'N° order'
    def get_produit_name(self, obj):
        return obj.commande.produit if obj.commande.produit else "N/A"
    get_produit_name.short_description = 'Product'
    def get_supplier_name(self, obj):
        return obj.commande.supplier if obj.commande.supplier else "N/A"
    get_supplier_name.short_description = 'Supplier'
    def get_commande_number(self, obj):
        return obj.id
    get_commande_number.short_description = 'N° Arrival'
  
    def get_commande_quantity_arrive(self, obj):
        return obj.quantity_arrive
    get_commande_quantity_arrive.short_description = 'Qte arrived'
    def get_quantity_transferred(self, obj):
        total_transferred = Transfer.objects.filter(Arrival=obj).aggregate(total=Sum('quantity'))
        return total_transferred['total'] or 0

    get_quantity_transferred.short_description = 'Transferred'  # Renaming the field in the admin

    

  # Register the action for the admin


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    actions = ['imprimer_pdf']
    list_display = ('id', 'name', 'address', 'phone', 'credit')
    search_fields = ('id', 'name', 'phone')
    list_filter = ('address', 'credit')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    actions = ['imprimer_pdf']
    list_display = ('id', 'name', 'address', 'phone', 'balance')
    search_fields = ('id', 'name', 'phone')
    list_filter = ('address', 'balance')

@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    actions = ['imprimer_pdf']
    list_display = ('id', 'designation','stock_list_link')
    search_fields = ('id', 'designation')
    

# @admin.register(Employee)
# class EmployeeAdmin(admin.ModelAdmin):
#     actions = ['imprimer_pdf']
#     list_display = ('id', 'name', 'address', 'phone', 'daily_salary', 'center')
#     search_fields = ('id', 'name', 'phone')
#     list_filter = ('center',)

# @admin.register(Purchase)
# class PurchaseAdmin(admin.ModelAdmin):
#     actions = ['imprimer_pdf']
#     list_display = ('product', 'supplier', 'purchase_date', 'quantity', 'unit_price', 'total_amount', 'payment_status', 'amount_paid')
#     search_fields = ('product__code', 'supplier__code', 'purchase_date')
#     list_filter = ('purchase_date', 'payment_status')

@admin.register(Transfer)
class MaterialTransferAdmin(admin.ModelAdmin):
    actions = ['imprimer_pdf']
    list_display = ('Arrival','get_commande_numbercommande', 'center', 'transfer_date', 'quantity', 'transfer_cost','get_produit_name')
    search_fields = ('product__code', 'center__code', 'transfer_date')
    list_filter = ('transfer_date',)
    def transfer_cost(self,obj):
        return obj.quantity*obj.Arrival.commande.unit_price
    def get_produit_name(self, obj):
        return obj.Arrival.commande.produit if obj.Arrival.commande.produit else "N/A"
    get_produit_name.short_description = 'Product'
    def get_commande_numbercommande(self, obj):
        return obj.Arrival.commande
    get_commande_numbercommande.short_description = 'N° order'

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    actions = ['imprimer_pdf']
    list_display = ('product', 'client','center', 'sale_date', 'quantity_sold', 'unit_price', 'total_amount', 'amount_paid')
    def total_amount(self,obj):
        return obj.quantity_sold * obj.unit_price
    search_fields = ('product__code', 'client__code', 'sale_date')
    list_filter = ('sale_date',)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    actions = ['imprimer_pdf']
    list_display = ('product', 'location', 'quantity_in_stock')
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

    # def get_queryset(self, request):
    #     # Override the queryset to filter based on the user's center
    #     queryset = super().get_queryset(request)
    #     queryset = queryset.filter(location="center1")
        

    #     return queryset

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    actions = ['imprimer_pdf']
    list_display = ('title', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'message')
    readonly_fields = ('created_at',)
    
# class PaymentCommandeForm(forms.ModelForm):
#     class Meta:
#         model = PaymentCommande
#         fields = '__all__'

#     def clean(self):
#         cleaned_data = super().clean()
#         montant = cleaned_data.get('montant')
#         commande = cleaned_data.get('commande')

#         if montant and commande:
#             calculated_limit = commande.unit_price * commande.quantity
#             if montant > calculated_limit:
#                 raise forms.ValidationError("Montant cannot exceed unit price multiplied by quantity.")
@admin.register(PaymentCommande)
class PaymentCommandeAdmin(admin.ModelAdmin):
    actions = ['imprimer_pdf']
    # form = PaymentCommandeForm
    list_display = ['commande', 'date', 'montant', 'obsrvation']
    search_fields = ['commande__id']  # Search by commande ID
    list_filter = ['date']
    def has_change_permission(self, request, obj=None):
        return False
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "commande":
            kwargs["queryset"] = Commande.objects.exclude(payed__in=[True])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
@admin.register(PaymentSupplier)
class PaymentSupplierAdmin(admin.ModelAdmin):
    actions = ['imprimer_pdf']
    # form = PaymentCommandeForm
    list_display = ['Supplier', 'date', 'montant', 'obsrvation']
    search_fields = ['Supplier__name']  # Search by commande ID
    list_filter = ['date']
@admin.register(PaymentCredit)
class PaymentSupplierAdmin(admin.ModelAdmin):
    actions = ['imprimer_pdf']
    # form = PaymentCommandeForm
    list_display = ['client', 'date', 'montant', 'obsrvation']
    search_fields = ['client__name']  # Search by commande ID
    list_filter = ['date']