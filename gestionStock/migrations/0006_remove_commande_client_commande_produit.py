# Generated by Django 4.2.3 on 2023-12-24 13:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestionStock', '0005_commande'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commande',
            name='client',
        ),
        migrations.AddField(
            model_name='commande',
            name='produit',
            field=models.ForeignKey(default=5, on_delete=django.db.models.deletion.CASCADE, to='gestionStock.product'),
            preserve_default=False,
        ),
    ]
