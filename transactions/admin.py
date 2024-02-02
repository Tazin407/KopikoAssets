from typing import Any
from django.contrib import admin
from .import models
# Register your models here.
# admin.site.register(models.Transaction)

admin.site.register(models.Bank)
admin.site.register(models.Transfer)

@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display= ['account', 'amount', 'balance_after_trans', 'transaction_type', 'loan_approve']
    
    # def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
    #     return super().save_model(request, obj, form, change)
    
    def save_model(self, request, obj, form, change):
        if obj.loan_approve:
            obj.account.balance += obj.amount
            obj.account.balance_after_trans= obj.account.balance
            obj.account.save()
            
        super().save_model(request, obj, form, change)
        