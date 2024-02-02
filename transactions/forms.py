from django import forms
from .models import Transaction
from .models import Bank, Transfer
from accounts.models import UserAccount
from django.contrib.auth.models import User


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'amount',
            'transaction_type'
        ]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account') # account value ke pop kore anlam
        super().__init__(*args, **kwargs)
        
        bank, created = Bank.objects.get_or_create(pk=1)
        if created:
            pass
       
        self.fields['transaction_type'].disabled = True # ei field disable thakbe
        self.fields['transaction_type'].widget = forms.HiddenInput() # user er theke hide kora thakbe

    def save(self, commit=True):
        
        self.instance.account = self.account
        self.instance.balance_after_trans = self.account.balance
        return super().save()



class TransferMoneyForm(forms.ModelForm):
    to_account_id= forms.IntegerField(label='Enter User Id')
    class Meta:
        model= Transfer
        fields=['to_account_id', 'amount']
        labels={
            'amount': 'Amount',
        }
        
    
        
    # def clean_to_account_id(self):
    #     user_id = self.cleaned_data.get('to_account_id')
    #     try:
    #         user= UserAccount.objects.get(account_no= user_id)
    #         self.instance.to_account= user
    #         return user
        
    #     except User.DoesNotExist:
    #         raise forms.ValidationError(f"User with {user_id} doesn't exist. Please enter the correct Id")
        
        
    # def clean_amount(self):
    #     amount= self.cleaned_data.get('amount')
    #     from_account= self.request.account
    #     if from_account is None:
    #         raise forms.ValidationError('Invalid account information.')
        
    #     balance= from_account.balance
        
    #     if amount > balance:
    #         raise forms.ValidationError(f'You can not send more than your current balance')
        
    #     return amount
            
        
        
        

class DepositForm(TransactionForm):
    def clean_amount(self): # amount field ke filter korbo
        min_deposit_amount = 100
        amount = self.cleaned_data.get('amount') # user er fill up kora form theke amra amount field er value ke niye aslam, 50
        
        
        
        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount} $'
            )

        return amount


class WithdrawForm(TransactionForm):

    def clean_amount(self):
        account = self.account
        min_withdraw_amount = 100
        max_withdraw_amount = 20000
        balance = account.balance # 1000
        amount = self.cleaned_data.get('amount')
        bank= Bank.objects.get(pk=1)
        
        totalasset=bank.totalAsset
        
        if amount > totalasset:
            raise forms.ValidationError(
                f'Bank is bankrupt.'
            )
        
        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at least {min_withdraw_amount} $'
            )

        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at most {max_withdraw_amount} $'
            )

        if amount > balance: # amount = 5000, tar balance ache 200
            raise forms.ValidationError(
                f'You have {balance} $ in your account. '
                'You can not withdraw more than your account balance'
            )

        return amount



class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        return amount





# from django import forms 
# from .import models

# class TransactionForm(forms.ModelForm):
#     class Meta:
#         model= models.Transaction
#         fields=['amount', 'transaction_type']
        
#     #transaction_type user dekbe na. eta hide korar jnno constructor e kaj korlam
#     def __init__(self, *args, **kwargs):
#         self.account= kwargs.pop('account')#kwargs theke account ke pop kore anlam 
#         #eta korle barbar user ke logged in proman korte hobe na
        
#         #pop er bodole get dileo hoito
        
#         super().__init__(*args, **kwargs)
#         self.fields['transaction_type'].disabled = True
#         self.fields['transaction_type'].widget= forms.HiddenInput()
        
#     def save(self, commit=True):
#         self.instance.account= self.account
#         self.instance.balance_after_trans= self.account.balance
        
#         return super().save()
    

# class DepositForm(TransactionForm):
#     def clean_amount(self): #amount ke filter korbo
#         minimum_amount=100
#         amount= self.cleaned_data.get('amount')
#         if amount < minimum_amount:
#             raise forms.ValidationError(
#                 f'You can not diposit less than {minimum_amount} BDT'
#             )
            
#         return amount
    
# class WithdrawForm(TransactionForm):
    
#     def clean_amount(self):
#         account= self.account #account ta ansi balance ber korar jnno
#         amount= self.cleaned_data.get('amount')
#         balance= account.balance
        
#         if amount > balance:
#             raise forms.ValidationError(
#                 f'You have only {balance} BDT left in your account.you can not withdraw more than your balance.'
#             )
            
#         return amount
    
# class LoanRequForm(TransactionForm):
    
#     def clean_amount(self):
#         amount= self.cleaned_data.get('amount')
        
#         return amount
    