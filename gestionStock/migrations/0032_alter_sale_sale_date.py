# Generated by Django 4.2.3 on 2024-01-21 22:25

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('gestionStock', '0031_client_date_of_registration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='sale_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
