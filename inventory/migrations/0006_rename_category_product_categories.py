# Generated by Django 4.1.7 on 2023-03-29 21:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_alter_product_slug'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='category',
            new_name='categories',
        ),
    ]
