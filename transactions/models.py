from django.db import models
from accounts.models import UserAccount
# Create your models here.
from .constants import TRANSACTION_TYPE

class Bank(models.Model):
    totalAsset= models.DecimalField(default=0, decimal_places=2, max_digits = 12)
    
class Transfer(models.Model):
    to_account= models.ForeignKey(UserAccount, related_name='to_account', on_delete=models.SET_NULL, null=True)
    amount= models.DecimalField(decimal_places=2, max_digits = 12)

class Transaction(models.Model):
    account = models.ForeignKey(UserAccount, related_name = 'transactions', on_delete = models.CASCADE) # ekjon user er multiple transactions hote pare
    
    amount = models.DecimalField(decimal_places=2, max_digits = 12)
    balance_after_trans = models.DecimalField(decimal_places=2, max_digits = 12)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE, null = True)
    timestamp = models.DateTimeField(auto_now_add=True)
    loan_approve = models.BooleanField(default=False) 
    
    class Meta:
        ordering = ['timestamp'] 




# from django.db import models
# from accounts.models import UserAccount
# from .import constants

# # Create your models here.
# class Transaction(models.Model):
#     account= models.ForeignKey(UserAccount, related_name = 'transactions', on_delete= models.CASCADE)
#     amount= models.DecimalField(decimal_places=2, max_digits=12)
#     transaction_type= models.CharField(max_length=20, choices=constants.TRANSACTION_CHOICES, blank=True)
#     balance_after_trans= models.DecimalField(decimal_places=2, max_digits=12)
    
#     timestamp= models.DateTimeField(auto_now_add=True)
#     loan_approve = models.BooleanField(default=False) 
    
#     class Meta:
#         ordering= ['timestamp']