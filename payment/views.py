from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import WithdrawalRequest, Balance, Payment
from .serializers import TransactionSerializer,WithdrawalListSerializer, WithdrawalSerializer, BalanceSerializer
from itertools import chain
from operator import attrgetter
import qrcode
from PIL import Image
from io import BytesIO
from django.http import HttpResponse
from django.conf import settings



@api_view(["GET"])
def get_qr_code(request):
    wallet_address = getattr(settings, "CRYPTO_WALLET_ADDRESS", None)
    
    if not wallet_address:
        return Response({"error": "Crypto wallet address is not configured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    qr = qrcode.make(wallet_address)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="image/png")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_history(request): 
    payments = Payment.objects.filter(user=request.user)
    serializer = TransactionSerializer(payments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction(request, pk): 
    payment = get_object_or_404(Payment, id=pk, user=request.user)
    serializer = TransactionSerializer(payment)
    return Response(serializer.data, status=status.HTTP_200_OK)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_balance(request):
    balance = get_object_or_404(Balance, user=request.user)
    serializer = BalanceSerializer(balance)
    return Response(serializer.data, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_withdrawal_request(request):
    serializer = WithdrawalSerializer(data=request.data, context={'user': request.user})

    if serializer.is_valid():
        withdrawal = serializer.save()
        return Response(
            {
                'message': 'Withdrawal request submitted successfully.',
                'data': WithdrawalSerializer(withdrawal).data
            }, 
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def withdrawal_list(request):
    withdrawals = WithdrawalRequest.objects.filter(user=request.user).order_by('-created_at')
    serializer = WithdrawalListSerializer(withdrawals, many=True)  
    return Response(serializer.data, status=status.HTTP_200_OK)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_transactions(request):
    # Fetch user withdrawals and payments
    withdrawals = WithdrawalRequest.objects.filter(user=request.user).order_by('-created_at')
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')

    # Combine transactions and sort by 'created_at'
    combined_transactions = sorted(
        chain(withdrawals, payments),
        key=attrgetter('created_at'),
        reverse=True
    )

    # Serialize data efficiently using list comprehension
    serialized_data = [
        (WithdrawalListSerializer(tx, context={'user': request.user}) if isinstance(tx, WithdrawalRequest) else TransactionSerializer(tx)).data
        for tx in combined_transactions
    ]

    return Response(serialized_data, status=status.HTTP_200_OK)







# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def all_transactions(request):
   
#     withdrawals = WithdrawalRequest.objects.filter(user=request.user).order_by('-created_at')
#     payments = Payment.objects.filter(user=request.user).order_by('-created_at')

#     # Combine both withdrawals and payments, then sort them by 'created_at' (newest first)
#     combined_transactions = sorted(
#         chain(withdrawals, payments),  # Combine both querysets using 'chain' to form a single iterable
#         key=attrgetter('created_at'),  # Sort the combined list by the 'created_at' attribute
#         reverse=True  # Sort in reverse order to show the most recent transactions first
#     )

#     # Initialize an empty list to store the serialized data
#     combined_serialized_data = []

#     # Loop through each transaction in the combined list
#     for transaction in combined_transactions:
#         if isinstance(transaction, WithdrawalRequest):
#             # If the transaction is a withdrawal, use the WithdrawalListSerializer
#             serializer = WithdrawalListSerializer(transaction, context={'user': request.user})
#         else:
#             # If the transaction is a payment, use the TransactionSerializer
#             serializer = TransactionSerializer(transaction)

#         # Append the serialized data of the transaction to the combined_serialized_data list
#         combined_serialized_data.append(serializer.data)

    
#     return Response(combined_serialized_data, status=status.HTTP_200_OK)
