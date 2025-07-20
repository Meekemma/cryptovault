from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import TransactionSerializer,WithdrawalListSerializer, WithdrawalSerializer, BalanceSerializer, PaymentSerializer,DailyInterestAccrualSerializer
from itertools import chain
from operator import attrgetter
import qrcode
from PIL import Image
from django.utils import timezone
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
    serializer = PaymentSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save(user=request.user)  # Attach the authenticated user
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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







@api_view(['POST'])
def trigger_interest(request):
    today = timezone.now().date()
    count = 0

    eligible_payments = Payment.objects.filter(status='completed', verified_by_admin=True, active_investment=True)

    for payment in eligible_payments:
        user = payment.user
        plan = payment.plan
        amount = payment.amount_paid
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
        if DailyInterestAccrual.objects.filter(user=user, date=today, payment=payment).exists():
            continue

        try:
            interest_config = Interest.objects.get(plan=plan)
        except Interest.DoesNotExist:
            continue

        percent = interest_config.daily_interest_percent
        daily_interest = (Decimal(percent) / 100) * amount

        DailyInterestAccrual.objects.create(user=user, date=today, amount=daily_interest, payment=payment)

        balance, _ = Balance.objects.get_or_create(user=user)
        balance.balance += daily_interest
        balance.save(update_fields=['balance'])

        count += 1

    return Response({"message": f"Interest applied to {count} users."})





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def daily_interest_accruals(request):
    accurals = DailyInterestAccrual.objects.select_related('user').filter(user=request.user)
    serializer = DailyInterestAccrualSerializer(accurals, many=True)
    return Response(serializer.data,  status=status.HTTP_200_OK)








