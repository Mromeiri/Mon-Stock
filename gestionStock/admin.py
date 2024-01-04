import os
from django.contrib import admin
from .models import *
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from gestionStock.Widgets import CustomForeignKeyRawIdFormField

from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from PIL import Image
from reportlab.lib.pagesizes import A4

def generate_pdf(products):
    buffer = BytesIO()

    # Create a canvas (PDF) with ReportLab
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Set up your logos (adjust the path as per your project structure)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path_left = BASE_DIR + '/static/img/favicon2.png'
    logo_path_right = BASE_DIR + '/static/img/favicon2.png'  # Add your right logo path

    logo_left = Image.open(logo_path_left)
    logo_right = Image.open(logo_path_right)

    # Draw logos on the PDF
    logo_width = 50
    logo_height = 50
    pdf.drawInlineImage(logo_left, 50, height - 100, width=logo_width, height=logo_height)
    pdf.drawInlineImage(logo_right, width - logo_width - 50, height - 100, width=logo_width, height=logo_height)

    # Set title
    pdf.setFont("Helvetica-Bold", 16)
    title = "La liste des produits"
    title_width = pdf.stringWidth(title, "Helvetica-Bold", 16)
    pdf.drawString((width - title_width) / 2, height - 75, title) 

    # Draw table header lines
    headers = ["Designation", "Type", "Quantity"]
    col_widths = [150, 100, 100]  # Adjust column widths as needed

    # Calculate total width of the table
    total_table_width = sum(col_widths)

    # Calculate starting x-coordinate to center the table horizontally
    start_x = (width - total_table_width) / 2

    # Set up table headers
    pdf.setFillColorRGB(0.5, 0.5, 0.8)  # Header color (adjust as needed)
    pdf.setFont("Helvetica-Bold", 12)  # Header font and size

    y = height - 150  # Starting Y-coordinate for the table header

    for i, header in enumerate(headers):
        pdf.drawString(start_x + sum(col_widths[:i]) + (col_widths[i] - pdf.stringWidth(header, "Helvetica-Bold", 12)) / 2, y, header)

    # Draw horizontal line for the table header
    pdf.line(start_x, y - 12, start_x + total_table_width, y - 12)  # Header border line

    # Set font and style for table content
    pdf.setFillColorRGB(0, 0, 0)  # Content color
    pdf.setFont("Helvetica", 10)  # Content font and size

    y_offset = height - 180  # Adjust the starting Y coordinate as needed

    # Iterate through products to create table rows
    for product in products:
        y_offset -= 20  # Adjust spacing between each product
        pdf.drawString(start_x, y_offset, product.designation)
        pdf.drawString(start_x + col_widths[0], y_offset, product.get_type_display)
        pdf.drawString(start_x + col_widths[0] + col_widths[1], y_offset, str(product.quantity_in_stock))  # Convert quantity to string

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    autocomplete_fields = ('produit',)
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
    list_display = ('get_commande_number','get_commande_numbercommande','date_arrive', 'get_commande_quantity_arrive','get_quantity_transferred', 'get_produit_name','get_supplier_name')
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

    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'designation','Type','quantity_in_stock','Avrege_quantity','image')  # Customize displayed fields
    search_fields = ('id', 'designation','Type','quantity_in_stock')
    actions = ['imprimer_pdf']

    def imprimer_pdf(self, request, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="products.pdf"'

        # Call the generate_pdf function passing the selected products
        pdf = generate_pdf(queryset)

        response.write(pdf.getvalue())
        return response

    imprimer_pdf.short_description = "Imprimer PDF"  # Register the action for the admin


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'phone', 'credit')
    search_fields = ('id', 'name', 'phone')
    list_filter = ('address', 'credit')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'phone', 'balance')
    search_fields = ('id', 'name', 'phone')
    list_filter = ('address', 'balance')

@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    list_display = ('id', 'designation','stock_list_link')
    search_fields = ('id', 'designation')
    

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'phone', 'daily_salary', 'center')
    search_fields = ('id', 'name', 'phone')
    list_filter = ('center',)

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('product', 'supplier', 'purchase_date', 'quantity', 'unit_price', 'total_amount', 'payment_status', 'amount_paid')
    search_fields = ('product__code', 'supplier__code', 'purchase_date')
    list_filter = ('purchase_date', 'payment_status')

@admin.register(Transfer)
class MaterialTransferAdmin(admin.ModelAdmin):
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
    list_display = ('product', 'client', 'sale_date', 'quantity_sold', 'unit_price', 'total_amount', 'amount_paid')
    def total_amount(self,obj):
        return obj.quantity_sold * obj.unit_price
    search_fields = ('product__code', 'client__code', 'sale_date')
    list_filter = ('sale_date',)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display=('product','location','quantity_in_stock')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
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
    # form = PaymentCommandeForm
    list_display = ['commande', 'date', 'montant', 'obsrvation']
    search_fields = ['commande__id']  # Search by commande ID
    list_filter = ['date']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "commande":
            kwargs["queryset"] = Commande.objects.exclude(payed__in=[True])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
@admin.register(PaymentSupplier)
class PaymentSupplierAdmin(admin.ModelAdmin):
    # form = PaymentCommandeForm
    list_display = ['Supplier', 'date', 'montant', 'obsrvation']
    search_fields = ['Supplier__name']  # Search by commande ID
    list_filter = ['date']
@admin.register(PaymentCredit)
class PaymentSupplierAdmin(admin.ModelAdmin):
    # form = PaymentCommandeForm
    list_display = ['client', 'date', 'montant', 'obsrvation']
    search_fields = ['client__name']  # Search by commande ID
    list_filter = ['date']