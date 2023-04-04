# Generated by Django 4.1.7 on 2023-04-03 21:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_alter_productinventory_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productinventory',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventories', to='inventory.product'),
        ),
    ]