# Generated by Django 4.1.7 on 2023-04-05 14:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0008_alter_productinventory_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productimage',
            name='product_inventory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='inventory.productinventory'),
        ),
    ]
