# Generated by Django 4.2.7 on 2024-01-27 07:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0006_rename_to_account_transfer_to_account_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transfer',
            old_name='from_account',
            new_name='account',
        ),
        migrations.RenameField(
            model_name='transfer',
            old_name='to_account_id',
            new_name='to_account',
        ),
    ]