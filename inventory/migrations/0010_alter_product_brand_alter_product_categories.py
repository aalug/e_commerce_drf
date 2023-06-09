# Generated by Django 4.1.7 on 2023-04-07 00:46

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_alter_productimage_product_inventory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='product', to='inventory.brand'),
        ),
        migrations.AlterField(
            model_name='product',
            name='categories',
            field=mptt.fields.TreeManyToManyField(related_name='product', to='inventory.category'),
        ),
    ]
