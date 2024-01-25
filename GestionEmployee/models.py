from django.db import models
from django.utils import timezone
from gestionStock.models import Center
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta, date
from django.db.models.signals import post_save, post_delete
# models.py


class Employee(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    daily_salary = models.DecimalField(max_digits=10, decimal_places=2)
    center = models.ForeignKey(Center, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        today = date.today()
        end_of_year = date(today.year, 12, 31)

        for month in range(today.month, 13):
            if month == 12:
                # Calculate days until the end of the current year
                days_in_month = (end_of_year - date(today.year, month, 1)).days
            else:
                # Calculate days until the end of the current month
                days_in_month = (date(today.year, month + 1, 1) - date(today.year, month, 1)).days
            
            salaie_amount = self.daily_salary * days_in_month

            Salaire.objects.create(
                employee=self,
                date=date(today.year, month, 1),
                salaire=salaie_amount
            )
    def __str__(self):
        return f"{self.name} " 

class Absence(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    

class AdvanceRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    request_date = models.DateField()
    def save(self, *args, **kwargs):
        # Call the parent class's save method
        employe = self.employee
        date_request = self.request_date

        # Recherche du salaire en fonction du mois, de l'année et de l'employé
        salaire = Salaire.objects.get(
            employee=employe,
            date__year=date_request.year,
            date__month=date_request.month
        )

        # Call the parent class's save method
        super().save(*args, **kwargs)

        Advance = AdvanceRequest.objects.get(pk=self.pk)
        print(Advance)
        if Advance.pk:
            salaire.salaire += Advance.amount
            salaire.save()

        # Adjust the Salaire based on the change in amount
        salaire.salaire -= self.amount
        salaire.save()
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
@receiver(post_save, sender=AdvanceRequest)
def update_salaire(sender, instance, **kwargs):
    # Check if the instance is being created (not updated)
    if kwargs.get('created', False):
        # Get the year and month from the request_date
        year_month = instance.request_date.strftime('%Y-%m')

        # Check if there is an existing Salaire record for the employee and year/month
        try:
            salaire_record = Salaire.objects.get(employee=instance.employee, date__startswith=year_month)
        except Salaire.DoesNotExist:
            # If there is no Salaire record, create one
            salaire_record = Salaire(employee=instance.employee, date=year_month + "-01", salaire=0)

        # Update the Salaire record with the new amount
        salaire_record.salaire -= instance.amount
        salaire_record.save()

# @receiver(post_save, sender=AdvanceRequest)
# def update_salaire_on_advance(sender, instance, created, **kwargs):
#     employe = instance.employee
#     date_request = instance.request_date

#     # Recherche du salaire en fonction du mois, de l'année et de l'employé
#     salaire = Salaire.objects.get(
#         employee=employe,
#         date__year=date_request.year,
#         date__month=date_request.month
#     )
#     Advance = AdvanceRequest.objects.get(
#         pk=instance.pk
#     )
#     print(Advance)
#     if Advance.pk:
#         print("1111")
#         salaire.salaire += Advance.amount
#     print("22222")   
#     salaire.salaire -= instance.amount

#     salaire.save()

@receiver(post_delete, sender=AdvanceRequest)
def delete_AdvanceRequest(sender, instance, **kwargs):
    employe = instance.employee
    date_request = instance.request_date

    # Use get() with a default parameter to handle the case when Salaire does not exist
    salaire, created = Salaire.objects.get_or_create(
        employee=employe,
        date__year=date_request.year,
        date__month=date_request.month,
        defaults={'salaire': 0}  # Set a default value if the object is created
    )

    print(salaire)
    if created:
        # If a new Salaire object is created, initialize its salaire field
        salaire.salaire = employe.daily_salary
    else:
        salaire.salaire += instance.amount

    salaire.save()