from django.db import models
from django.utils import timezone
from gestionStock.models import Center
from django.db.models.signals import post_save
from django.dispatch import receiver

# models.py


class Employee(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    daily_salary = models.DecimalField(max_digits=10, decimal_places=2)
    center = models.ForeignKey(Center, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

class Absence(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    

class AdvanceRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    request_date = models.DateField()

class ActivityLog(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=255)
    details = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

class Salaire(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    salaire = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ['employee', 'date']
# Signal receiver function to create Salaire instance for each new month
@receiver(post_save, sender=Employee)
def create_salaire_instance(sender, instance, created, **kwargs):
    if created:
        current_date = timezone.now()
        # Check if a Salaire instance for the current month exists
        existing_salaire = Salaire.objects.filter(employee=instance, date__month=current_date.month, date__year=current_date.year).first()
        
        if not existing_salaire:
            # If not, create a new Salaire instance
            Salaire.objects.create(employee=instance, date=current_date, salaire=0)