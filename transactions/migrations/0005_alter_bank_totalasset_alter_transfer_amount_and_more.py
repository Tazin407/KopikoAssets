# Generated by Django 4.2.7 on 2024-01-26 12:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('transactions', '0004_bank_transfer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bank',
            name='totalAsset',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AlterField(
            model_name='transfer',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
        migrations.AlterField(
            model_name='transfer',
            name='from_account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='from_account', to='accounts.useraccount'),
        ),
        migrations.AlterField(
            model_name='transfer',
            name='to_account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='to_account', to='accounts.useraccount'),
        ),
    ]