from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import PaymentSerializer,TransactionSerializer
from django_coinpayments.models import Payment
from django_coinpayments.exceptions import CoinPaymentsProviderError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status as http_status
from .models import WithdrawalRequest,Balance
from .serializers import WithdrawalSerializer,WithdrawalListSerializer,BalanceSerializer
from django.utils.datastructures import MultiValueDictKeyError
from itertools import chain
from operator import attrgetter




from decimal import Decimal
@method_decorator(csrf_exempt, name='dispatch')
class CreatePaymentView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save(
                user=request.user,  # Set the user field
                amount_paid=Decimal(0), 
                status=Payment.PAYMENT_STATUS_PROVIDER_PENDING
            )
            # Ensure the buyer_email is correctly passed for transaction creation
            buyer_email = payment.user.email
            try:
                transaction = payment.create_tx(buyer_email=buyer_email)
                return Response({'checkout_url': transaction.status_url}, status=status.HTTP_201_CREATED)
            except CoinPaymentsProviderError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







@method_decorator(csrf_exempt, name='dispatch')
class CoinPaymentsIPNView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.POST
        
        txn_id = data.get('txn_id')
        status_code = int(data.get('status', 0))  
        amount = Decimal(data.get('amount1', '0'))
        currency = data.get('currency1')

        try:
            payment = Payment.objects.get(provider_tx__id=txn_id)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=http_status.HTTP_404_NOT_FOUND)

        if status_code >= 100 or status_code == 2:
            payment.status = Payment.PAYMENT_STATUS_PAID
            payment.amount_paid = amount
        elif status_code < 0:
            payment.status = Payment.PAYMENT_STATUS_CANCELLED
        else:
            payment.status = Payment.PAYMENT_STATUS_PENDING
        
        payment.save()
        return Response({'message': 'Payment status updated'}, status=http_status.HTTP_200_OK)






@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_history(request): 
    payments= Payment.objects.filter(user=request.user)
    serializer =TransactionSerializer(payments,many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction(request, pk): 
    try:
        payment = Payment.objects.get(id=pk, user=request.user)
    except Payment.DoesNotExist:
        return Response({'message': 'Payment not Found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TransactionSerializer(payment)
    return Response(serializer.data, status=status.HTTP_200_OK)







@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_balance(request):
    try:
        balance = Balance.objects.get(user=request.user)
        serializer = BalanceSerializer(balance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Balance.DoesNotExist:
        return Response({'error': 'Balance not found'}, status=status.HTTP_404_NOT_FOUND)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_withdrawal_request(request):
    serializer = WithdrawalSerializer(data=request.data, context={'user': request.user})
    if serializer.is_valid():
        withdrawal = serializer.save()
        return Response({'message': 'Withdrawal request submitted successfully.'}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






@api_view(['GET'])
@permission_classes([IsAuthenticated])
def withdrawal_list(request):
    withdrawals = WithdrawalRequest.objects.filter(user=request.user).order_by('-created_at')
    serializer = WithdrawalListSerializer(withdrawals, many=True, context={'user': request.user})
    
    return Response(serializer.data, status=status.HTTP_200_OK)







@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_transactions(request):
   
    withdrawals = WithdrawalRequest.objects.filter(user=request.user).order_by('-created_at')
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')

    # Combine both withdrawals and payments, then sort them by 'created_at' (newest first)
    combined_transactions = sorted(
        chain(withdrawals, payments),  # Combine both querysets using 'chain' to form a single iterable
        key=attrgetter('created_at'),  # Sort the combined list by the 'created_at' attribute
        reverse=True  # Sort in reverse order to show the most recent transactions first
    )

    # Initialize an empty list to store the serialized data
    combined_serialized_data = []

    # Loop through each transaction in the combined list
    for transaction in combined_transactions:
        if isinstance(transaction, WithdrawalRequest):
            # If the transaction is a withdrawal, use the WithdrawalListSerializer
            serializer = WithdrawalListSerializer(transaction, context={'user': request.user})
        else:
            # If the transaction is a payment, use the TransactionSerializer
            serializer = TransactionSerializer(transaction)

        # Append the serialized data of the transaction to the combined_serialized_data list
        combined_serialized_data.append(serializer.data)

    
    return Response(combined_serialized_data, status=status.HTTP_200_OK)
