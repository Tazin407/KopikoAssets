from django.urls import path
from .views import DepositView, WithdrawView, LoanListView, LoanRequView, TransactionReportView, PayLoanView,TransferView

urlpatterns = [
    path('deposit/', DepositView.as_view(), name='deposit_money'),
    path('withdraw/', WithdrawView.as_view(), name='withdraw_money'),
    path('report/', TransactionReportView.as_view(), name='transaction_report'),
    path('loan_request/', LoanRequView.as_view(), name='loan_request'),
    path('pay_loan/', PayLoanView.as_view(), name='pay_loan'),
    path('loan_list/', LoanListView.as_view(), name='loan_list'),
    path('transfer_form/', TransferView.as_view(), name='transfer_form'),
   
]

