# Generated by Django 5.0.6 on 2024-06-03 02:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_user_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.PositiveSmallIntegerField(blank=True, choices=[('VENDOR', 'Vendor'), ('CUSTOMER', 'Customer')], null=True),
        ),
    ]