from django.urls import path
from .views import CreatePaymentView,CoinPaymentsIPNView
from . import views

urlpatterns = [
    path('create-payment/', CreatePaymentView.as_view(), name='create-payment'),
    path('ipn/', CoinPaymentsIPNView.as_view(), name='ipn'),
    path('transactions/', views.transaction_history, name='transactions'),
    path('transaction/<str:pk>/', views.transaction, name='transaction'),
    path('total_balance/', views.user_balance, name='total_balance'),

    path('withdrawal/', views.create_withdrawal_request, name='withdrawal'),
    path('withdrawal_history/', views.withdrawal_list, name='withdrawal_history'),
    path('all_transaction/', views.all_transactions,name='all_transaction')

]

