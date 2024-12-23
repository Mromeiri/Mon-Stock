from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models.signals import post_delete
from django.utils.timezone import now

TYPE_CHOICES = (
        ('1', 'Matieres Premiére'),
        ('2', 'Final'),
    )
Notification_label = (
        ('Out of stock', 'Out of stock'),
        
    )
COMMANDE_STATE_CHOICES = (
    ('1', 'En attente'),
    
  
    
    ('3', 'Livrée'),
    ('4', 'Annulée'),
    
    ('2', 'Partiellement arrivée'),
)
class Product(models.Model):
    designation = models.CharField(max_length=100)
    Type = models.CharField(max_length=1, choices=TYPE_CHOICES, null=True, blank=True)
    quantity_in_stock= models.PositiveIntegerField( default=0)
    Avrege_quantity= models.PositiveIntegerField( default=0)
    image = models.ImageField(upload_to='static/img/', null=True, blank=True)
    def __str__(self):
        return f"{self.designation} " 
    def create_stock_for_centers(self):
        centers = Center.objects.all()
        for center in centers:
            Stock.objects.get_or_create(product=self, location=center)
    @property
    def get_type_display(self):
        return dict(TYPE_CHOICES).get(self.Type, 'Undefined')
    def get_pourcentage(self):
        if self.quantity_in_stock > self.Avrege_quantity * 2:
            return 100

        if self.Avrege_quantity != 0:
            percentage = int((self.quantity_in_stock * 100) / (self.Avrege_quantity * 2))
            # Round the percentage to the nearest multiple of 5
            rounded_percentage = ((percentage + 2) // 5) * 5  # Adding 2 for rounding purposes
            return rounded_percentage if rounded_percentage <= 100 else 100

        return 0

           

    # Autres champs pour la description du produit
@receiver(post_save, sender=Product)
def create_stock_for_product(sender, instance, created, **kwargs):
    if created:
        instance.create_stock_for_centers()
class Client(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    credit = models.DecimalField(max_digits=10, decimal_places=2)
    date_of_registration = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} " 
    # Autres champs pour les détails du client

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"{self.name} " 
    # Autres champs pour les détails du fournisseur

class Commande(models.Model):
    supplier = models.ForeignKey(Supplier,  on_delete=models.CASCADE)
    produit = models.ForeignKey(Product,  on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    state = models.CharField(max_length=1, choices=COMMANDE_STATE_CHOICES, default='1' )
    date_created = models.DateTimeField(default=timezone.now)
    payed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.id} " 

class ArriveInStock(models.Model):
     
    commande = models.ForeignKey(Commande,  on_delete=models.CASCADE)
    date_arrive = models.DateTimeField(default=timezone.now)
    quantity_arrive = models.PositiveIntegerField()
    def clean(self):
        # Get the total quantity arrived for this Commande
        sum_quantity_arrive = ArriveInStock.objects.filter(commande=self.commande).aggregate(total_quantity=Sum('quantity_arrive'))

        # Calculate the new total quantity arrived if this instance is being changed
        total_quantity_arrived = sum_quantity_arrive['total_quantity'] or 0

        if total_quantity_arrived + self.quantity_arrive > self.commande.quantity:
            raise ValidationError("The total quantity arrived cannot exceed the ordered quantity.")
       
        
    def save(self, *args, **kwargs):
        # Validate quantity_arrive before saving
        self.clean()

        # Call the parent class's save method
        super(ArriveInStock, self).save(*args, **kwargs)

        # Get the total quantity arrived for this Commande
        sum_quantity_arrive = ArriveInStock.objects.filter(commande=self.commande).aggregate(total_quantity=Sum('quantity_arrive'))
        total_quantity_arrived = sum_quantity_arrive['total_quantity'] or 0
        product = self.commande.produit
        if product:
            product.quantity_in_stock += self.quantity_arrive
            product.save()
        
        if total_quantity_arrived == self.commande.quantity:
            # Update the related Commande's state to '3' if the total quantity arrived matches the ordered quantity
            self.commande.state = '3'
            self.commande.save()
        else:
            # Update the related Commande's state to '2'
            self.commande.state = '2'
            self.commande.save()
    def __str__(self):
        return f"Lot{self.id}  {self.commande.produit} " 

class Center(models.Model):
    designation = models.CharField(max_length=100)
    # Autres champs pour les détails du centre
    def __str__(self):
        return f"{self.designation} " 
    def create_stock_for_products(self):
        products = Product.objects.all()
        for product in products:
            Stock.objects.get_or_create(product=product, location=self)
    
    def stock_list_link(self):
        url = reverse('admin:gestionStock_stock_changelist')  # Replace 'yourapp' with your app name
        url += f'?location__id__exact={self.id}'
        return mark_safe(f'<a href="{url}">LOOK</a>')

    stock_list_link.short_description = 'Stock List'

@receiver(post_save, sender=Center)
def create_stock_for_center(sender, instance, created, **kwargs):
    if created:
        instance.create_stock_for_products()

# class Employee(models.Model):
#     name = models.CharField(max_length=100)
#     address = models.CharField(max_length=200)
#     phone = models.CharField(max_length=20)
#     daily_salary = models.DecimalField(max_digits=10, decimal_places=2)
#     center = models.ForeignKey(Center, on_delete=models.CASCADE)
    # Autres champs pour les détails de l'employé

# class Purchase(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
#     purchase_date = models.DateField()
#     quantity = models.PositiveIntegerField()
#     unit_price = models.DecimalField(max_digits=10, decimal_places=2)
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_status = models.BooleanField(default=False)
#     amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    # Autres champs pour les détails de l'achat

class Transfer(models.Model):
    Arrival = models.ForeignKey(ArriveInStock, on_delete=models.CASCADE)
    center = models.ForeignKey(Center, on_delete=models.CASCADE)
    transfer_date = models.DateTimeField(default=timezone.now)
    quantity = models.PositiveIntegerField()
    # Autres champs pour les détails du transfert
    def save(self, *args, **kwargs):
          # Only update on new Transfer creation
            stock = Stock.objects.filter(
                product=self.Arrival.commande.produit,
                location=self.center
            ).first()
            if stock:
                print(stock)
                stock.quantity_in_stock += self.quantity
                stock.save()
            else:
                Stock.objects.create(
                    product=self.Arrival.commande.produit,
                    location=self.center,
                    quantity_in_stock=self.quantity
                )
            super(Transfer, self).save(*args, **kwargs)
    def delete(self, *args, **kwargs):
            stock = Stock.objects.filter(
                product=self.Arrival.commande.produit,
                location=self.center
            ).first()
            if stock:
                print(stock)
                stock.quantity_in_stock -= self.quantity
                stock.save()
           
    def clean(self):
        # Get the total quantity arrived for this Commande
        sum_quantity = Transfer.objects.filter(Arrival=self.Arrival).aggregate(total_quantity=Sum('quantity'))
        

        # Calculate the new total quantity arrived if this instance is being changed
        total_quantity_exiqt = sum_quantity['total_quantity'] or 0

        if total_quantity_exiqt + self.quantity > self.Arrival.quantity_arrive:
            raise ValidationError("The total quantity arrived cannot exceed the ordered quantity.")
       

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    center = models.ForeignKey(Center, on_delete=models.SET_NULL, null=True, blank=True)
    sale_date = models.DateTimeField(default=now)
    quantity_sold = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def clean(self):
        total_amount = self.unit_price * self.quantity_sold
        if self.amount_paid > total_amount :
            raise ValidationError("Amount paid cannot exceed the total amount.")
        if self.product.quantity_in_stock <= self.quantity_sold:
            Notification.objects.create(
                title="Out of stock",
                message=f"The product {self.product} is insufficient."
            )
            raise ValidationError("Qte not enough.")
    def save(self, *args, **kwargs):
        print(self.pk)
        
        if self.pk != None:
            print("heelllllll")
            existing_sale = Sale.objects.get(pk=self.pk)
            print(existing_sale)
            # Update the client's credit by reverting the previous difference
            existing_difference = existing_sale.unit_price * existing_sale.quantity_sold - existing_sale.amount_paid
            existing_sale.client.credit -= existing_difference 
            new_total_amount = self.unit_price * self.quantity_sold
            new_difference = new_total_amount - self.amount_paid
            self.client.credit = new_difference + existing_sale.client.credit
            self.client.save()
            existing_stock = existing_sale.product.quantity_in_stock +existing_sale.quantity_sold
            self.product.quantity_in_stock = existing_stock -self.quantity_sold
            self.product.save()

            
        else:
            self.product.quantity_in_stock -=self.quantity_sold
            self.product.save()
            total_amount = self.unit_price * self.quantity_sold
            difference = total_amount - self.amount_paid
            if difference > 0:
                client = self.client
                client.credit = client.credit + difference
                client.save()

        super(Sale, self).save(*args, **kwargs)
@receiver(post_delete, sender=Sale)
def update_client_balance_on_delete(sender, instance, **kwargs):
        instance.product.quantity_in_stock +=instance.quantity_sold
        instance.product.save()
        total_amount = instance.unit_price * instance.quantity_sold
        difference = total_amount - instance.amount_paid
        if difference > 0:
            client = instance.client
            client.credit = client.credit  - difference
            client.save()

class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    location = models.ForeignKey(Center, on_delete=models.CASCADE)
    quantity_in_stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [['product', 'location']]

    def __str__(self):
        return f"{self.product} {self.location}"

class Notification(models.Model):

    title = models.CharField(max_length=100,choices=Notification_label)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.title
from django.db.models import F
class PaymentCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    montant = models.PositiveIntegerField()
    obsrvation = models.CharField( max_length=50,blank=True,null=True)
    
    def clean(self):
        commande = self.commande
        if self.montant > commande.unit_price * commande.quantity:
            raise ValidationError("Montant cannot exceed unit price multiplied by quantity.")
    def save(self, *args, **kwargs):
        commande = self.commande
        commande.payed = True
        
        difference = (commande.unit_price * commande.quantity) - self.montant
        if difference > 0:
            supplier = commande.supplier
            supplier.balance = supplier.balance + difference
            supplier.save()
        commande.save()
        # Save PaymentCommande instance
        super(PaymentCommande, self).save(*args, **kwargs)
    
@receiver(post_delete, sender=PaymentCommande)
def adjust_supplier_balance_on_delete(sender, instance, **kwargs):
    commande = instance.commande
    commande.payed = False
    difference = (commande.unit_price * commande.quantity) - instance.montant
    if difference > 0:
        supplier = commande.supplier
        supplier.balance = supplier.balance  - difference
        supplier.save()
    commande.save()

class PaymentSupplier(models.Model):
    Supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    montant = models.PositiveIntegerField()
    obsrvation = models.CharField( max_length=50,blank=True,null=True)
    def save(self, *args, **kwargs):
        print(self.pk)
        
        if self.pk != None:
            print("heelllllll")
            original_instance = PaymentSupplier.objects.get(pk=self.pk)
            
            montant_difference = self.montant - original_instance.montant

        # Update the supplier's balance with the montant difference
            self.Supplier.balance -= montant_difference
            self.Supplier.save()
        

        super(PaymentSupplier, self).save(*args, **kwargs)

        
@receiver(post_save, sender=PaymentSupplier)
def update_supplier_balance_on_save(sender, instance, created, **kwargs):
    if created:  # Check if a new PaymentSupplier instance is created
        Supplier = instance.Supplier
        Supplier.balance -= instance.montant
        Supplier.save()
    

@receiver(post_delete, sender=PaymentSupplier)
def update_supplier_balance_on_delete(sender, instance, **kwargs):
    Supplier = instance.Supplier
    Supplier.balance += instance.montant
    Supplier.save()

class PaymentCredit(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    montant = models.PositiveIntegerField()
    obsrvation = models.CharField( max_length=50,blank=True,null=True)
  
    def save(self, *args, **kwargs):
        print(self.pk)
        
        if self.pk != None:
            print("heelllllll")
            existing_sale = PaymentCredit.objects.get(pk=self.pk)
            
            # Update the client's credit by reverting the previous difference
            existing_difference = existing_sale.montant 
            existing_sale.client.credit += existing_difference
            

            self.client.credit =  existing_sale.client.credit - self.montant 
            self.client.save()
        else:
            
                client = self.client
                client.credit = client.credit - self.montant
                client.save()

        super(PaymentCredit, self).save(*args, **kwargs)
@receiver(post_delete, sender=PaymentCredit)
def update_supplier_balance_on_delete(sender, instance, **kwargs):
                client = instance.client
                client.credit = client.credit + instance.montant
                client.save()