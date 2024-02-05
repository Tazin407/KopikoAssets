from typing import Any
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.http import HttpResponse
from django.views.generic import CreateView, ListView
from transactions.constants import DEPOSIT, WITHDRAWAL,LOAN, LOAN_PAID, TRANSFER, RECIEVED
from datetime import datetime
from django.db.models import Sum
from .models import Bank, Transfer
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from transactions.forms import (
    DepositForm,
    WithdrawForm,
    LoanRequestForm,
    TransferMoneyForm
)
from transactions.models import Transaction


        # message= render_to_string('email_message.html', {
        #     "user": self.request.user,
        #     "amount" : amount,
        #     "transaction" : diposit,
        # })
        # to_email= self.request.user.email
        # send_email= EmailMultiAlternatives(mail_subject, '', to=[to_email])
        # send_email.attach_alternative(message, 'text/html')
        # send_email.send()
        

def send_email(user, amount, transaction, to_email):
    mail_subject="Transaction Message"
    message= render_to_string('email_message.html', {
        "user": user,
        "amount" : amount,
        "transaction": transaction,
    })
    send_email= EmailMultiAlternatives(mail_subject,'', to=[to_email] )
    send_email.attach_alternative(message, 'text/html')
    send_email.send()

class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transaction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # template e context data pass kora
        context.update({
            'title': self.title
        })

        return context


class DepositView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit'

    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        bank= Bank.objects.get(pk=1)
        account = self.request.user.account
        # if not account.initial_deposit_date:
        #     now = timezone.now()
        #     account.initial_deposit_date = now
        account.balance += amount # amount = 200, tar ager balance = 0 taka new balance = 0+200 = 200
        bank.totalAsset +=amount
        account.save(
            update_fields=[
                'balance'
            ]
        )
        
        bank.save()

        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully'
        )
        
        send_email(self.request.user, amount, 'diposit', self.request.user.email)

        return super().form_valid(form)


class WithdrawView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw Money'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        bank= Bank.objects.get(pk=1)
        bank.totalAsset-=amount
        self.request.user.account.balance -= form.cleaned_data.get('amount')
        bank.save()
        # balance = 300
        # amount = 5000
        self.request.user.account.save(update_fields=['balance'])

        messages.success(
            self.request,
            f'Successfully withdrawn {"{:,.2f}".format(float(amount))}$ from your account'
        )
        send_email(self.request.user, amount, 'withdraw', self.request.user.email)

        return super().form_valid(form)

class LoanRequView(TransactionCreateMixin):
    form_class = LoanRequestForm
    title = 'Request For Loan'

    def get_initial(self):
        initial = {'transaction_type': LOAN}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        current_loan_count = Transaction.objects.filter(
            account=self.request.user.account,transaction_type=3,loan_approve=True).count()
        if current_loan_count >= 3:
            return HttpResponse("You have cross the loan limits")
        messages.success(
            self.request,
            f'Loan request for {"{:,.2f}".format(float(amount))}$ submitted successfully'
        )

        return super().form_valid(form)
    
class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transaction_report.html'
    model = Transaction
    balance = 0 # filter korar pore ba age amar total balance ke show korbe
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            queryset = queryset.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)
            self.balance = Transaction.objects.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date
            ).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance
       
        return queryset.distinct() # unique queryset hote hobe
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account
        })

        return context
    
        
class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id=loan_id)
        print(loan)
        if loan.loan_approve:
            user_account = loan.account
                # Reduce the loan amount from the user's balance
                # 5000, 500 + 5000 = 5500
                # balance = 3000, loan = 5000
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.loan_approved = True
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect('transactions:loan_list')
            else:
                messages.error(
            self.request,
            f'Loan amount is greater than available balance'
        )

        return redirect('loan_list')


class LoanListView(LoginRequiredMixin,ListView):
    model = Transaction
    template_name = 'transactions/loan_request.html'
    context_object_name = 'loans' # loan list ta ei loans context er moddhe thakbe
    
    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(account=user_account,transaction_type=3)
        print(queryset)
        return queryset

from accounts.models import UserAccount
class TransferView(LoginRequiredMixin,View):
    template_name= 'transfer_form.html'
    
    def get(self, request):
        form = TransferMoneyForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form= TransferMoneyForm(request.POST)
        if form.is_valid():
            try:
                from_account= self.request.user.account
                to_account_id= form.cleaned_data.get('to_account_id')
                to_account= UserAccount.objects.get(account_no= to_account_id)
                amount= form.cleaned_data.get('amount')

                
            except UserAccount.DoesNotExist:
                messages.error(request, f"Account doesn't exist. Please enter carefully")
                return redirect('transfer_form')
            
            if from_account.balance < amount:
                messages.error(request, f"You can't transfer more than your current balance")
                return redirect('transfer_form')
            
            else:
                
                from_account.balance-= amount
                from_account.save()
                to_account.balance += amount
                to_account.save()
                
                
                Transaction.objects.create(
                    account= from_account,
                    amount= amount,
                    balance_after_trans= from_account.balance,
                    transaction_type = TRANSFER
                )
                Transaction.objects.create(
                    account= to_account,
                    amount= amount,
                    balance_after_trans= to_account.balance,
                    transaction_type = RECIEVED
                )
                
                messages.success(request, f"Transfer Successful")
                return redirect('profile')
            
        return render(request, self.template_name, {'form': form})
    
    
    
    
    # def get_initial(self) -> dict[str, Any]:
    #     initial= {'from_account': self.request.user.account}
    #     return initial
        
    # def form_valid(self, form):
    #     from_account= self.request.user.account
    #     # to_account_id= form.cleaned_data.get('to_account_id')
    #     to_account= form.cleaned_data.get('to_account')
    #     amount= form.cleaned_data.get('amount')
        
    #     from_account.balance-=amount
    #     to_account.balance +=amount
    #     messages.success( self.request, f"Money Transfer Successful")
        
    #     return super().form_valid(form)
    











# from typing import Any
# from django.shortcuts import render, redirect, get_list_or_404
# from datetime import datetime
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.views.generic import CreateView, ListView, View
# from django.urls import reverse_lazy
# from .import models
# from .import forms
# from django.db.models import Sum
# from django.contrib import messages
# from django.http import HttpResponse
# from transactions.constants import DEPOSIT, WITHDRAWAL,LOAN, LOAN_PAID


# class TransactionCreateMixin(LoginRequiredMixin, CreateView):
#     model= models.Transaction
#     title= ''
#     template_name= 'transaction_form.html'
#     success_url = reverse_lazy('deposit_money')
    
#     # def get_form_kwargs(self) -> dict[str, Any]:
#     #     return super().get_form_kwargs()
    
#     #eta form er init e account ke pass korbe
#     def get_form_kwargs(self):
#         kwargs= super().get_form_kwargs()
#         kwargs.update({
#             'account': self.request.user.account
#         })
#         return kwargs
    
#     # def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
#     #     return super().get_context_data(**kwargs)
    
#     #ei function ta nilam just title ta pass korar jonno 
#     def get_context_data(self, **kwargs):
#         context= super().get_context_data(**kwargs)
#         context.update({
#             'title': self.title
#         })

#         return context
    
# class DepositView(TransactionCreateMixin):
#     form_class=forms.DepositForm
#     title='Diposit Money'
#     print('Deposit')
    
#     def get_initial(self):
#         initial= {'transaction_type': DEPOSIT}
#         print(initial)
#         return initial
    
    
# #initial kete dewar por kaj korsilo

#     # def get_success_url(self):
#     #     print(self.request.path)
#     #     return self.request.path

#     def form_valid(self, form):
        
#         amount=form.cleaned_data.get('amount')
#         account= self.request.user.account
#         account.balance += amount
#         print(amount)
        
#         account.save(
#             update_fields=['balance']
#         )
#         print('Hello')
        
#         messages.success(self.request, f"{amount} BDT has been successfully deposited")
        
#         return super().form_valid(form)
    
      
    
# class WithdrawView(TransactionCreateMixin):
#     form_class= forms.WithdrawForm
#     title= 'Withdraw Money'
#     print('amount')
    
#     def get_success_url(self):
#         return self.request.path
    
#     def form_valid(self, form):
#         amount= form.cleaned_data['amount']
#         account= self.request.user.account
#         account.balance-=amount
        
#         account.save(
#             update_fields=['balance']
#         )
#         messages.success(self.request, f"{amount} BDT has been successfully withdrawed")
#         return super().form_valid(form)
    
    
# class LoanRequView(TransactionCreateMixin):
#     form_class= forms.LoanRequForm
#     title= 'Loan Request'
    
#     def get_initial(self):
#         initial= {'transaction_type': LOAN}
#         return initial
    
#     def form_valid(self, form):
#         amount= form.cleaned_data.get('amount')
#         current_loan_count= models.Transaction.objects.filter(account= self.request.user.account,
#             loan_approve=True,transaction_type= 'Loan').count()
        
#         if current_loan_count >=3:
#             return HttpResponse(f"You have reached your loan limit")
        
#         messages.success(self.request, f"{amount} BDT has been requested for loan. Please wait for the approval")
        
        
#         return super().form_valid(form)
    
# class TransactionReportView(LoginRequiredMixin, ListView):
#     model= models.Transaction
#     template_name ='transaction_report.html'
    
#     def get_queryset(self):
#         queryset= super().get_queryset().filter(
#             account= self.request.user.account
#         )
        
#         start_date_str= self.request.GET.get('start_date')
#         end_date_str= self.request.GET.get('end_date')
        
#         if start_date_str and end_date_str:
#             start_date= datetime.strptime(start_date_str, "%Y-%m-%d").date()
#             end_date= datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
#             queryset= queryset.filter(timestamp__date__gte= start_date, timestamp__date__lte=end_date)
#             self.balance= models.Transaction.objects.filter(timestamp__date__gte= start_date, timestamp__date__lte=end_date).aggregate(Sum('amount'))['amount__sum']
            
#         else:
#             self.balance= self.request.user.account.balance
            
#         return queryset.distinct()
    
#     def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
#         context= super().get_context_data(**kwargs)
#         context.update({
#             'account': self.request.user.account
#         })
#         return context
        
        
# class PayLoanView(LoginRequiredMixin, View):
#     def get(self, request, loan_id):
#         loan = get_list_or_404(models.Transaction, id= loan_id)
        
#         if loan.loan_approve:
#             user_account= loan.account
#             if loan.amount < user_account.balance:
#                 user_account.balance -= loan.amount
#                 loan.balance_after_transaction= user_account.balance
#                 user_account.save()
#                 loan.transaction_type= LOAN_PAID
#                 loan.save()
                
#                 return redirect('transaction_report')
#             else:
#                 messages.error(self.request, f'Not enough balance')
                
#         return redirect('transaction_report')
    
# class LoanListView(LoginRequiredMixin, ListView):
#     model= models.Transaction
#     context_object_name= 'loans'
    
#     def get_queryset(self):
#         user_account= self.request.user.account
#         queryset= models.Transaction.objects.filter(account= user_account, transaction_type= LOAN)
#         return queryset
        
    
    
    