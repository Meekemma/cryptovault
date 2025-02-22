from django.urls import path
from . import views

urlpatterns = [
    path("qr-code/", views.get_qr_code, name="get_qr_code"),
    path('create_payment/', views.create_payment, name='create_payment'),
    path('transactions/', views.transaction_history, name='transactions'),
    path('transaction/<str:pk>/', views.transaction, name='transaction'),
    path('total_balance/', views.user_balance, name='total_balance'),

    path('withdrawal/', views.create_withdrawal_request, name='withdrawal'),
    path('withdrawal_history/', views.withdrawal_list, name='withdrawal_history'),
    path('all_transaction/', views.all_transactions,name='all_transaction')

]
