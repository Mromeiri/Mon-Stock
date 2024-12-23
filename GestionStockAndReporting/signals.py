# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from datetime import datetime

from GestionEmployee.models import Salaire

@receiver(post_save, sender=User)
def create_salary_record(sender, instance, created, **kwargs):
    if created:
        current_month = datetime.now().strftime('%m-%Y')
        Salaire.objects.get_or_create(employee=instance, date=current_month)
