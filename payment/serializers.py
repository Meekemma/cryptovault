from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

from.models import WithdrawalRequest,Balance,Payment,DailyInterestAccrual


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'plan', 'amount_paid',
            'currency', 'transaction_id', 'status', 'created_at'
        ]
        read_only_fields = ['transaction_id', 'status', 'created_at']

    # Ensure amount is positive and greater than zero
    def validate_amount_paid(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount paid must be greater than zero.")
        return value

    # Validate plan against allowed choices
    def validate_plan(self, value):
        if value not in dict(Payment.PLAN_CHOICES):
            raise serializers.ValidationError("Invalid plan selected.")
        return value

    # Validate currency against allowed choices
    def validate_currency(self, value):
        if value not in dict(Payment.CURRENCY_CHOICES):
            raise serializers.ValidationError("Invalid currency selected.")
        return value

    # Cross-field validation based on selected plan and amount
    def validate(self, data):
        plan = data.get('plan')
        amount = data.get('amount_paid')

        # Plan-specific amount limits
        if plan == 'starter':
            if amount < 100:
                raise serializers.ValidationError("Minimum amount for the Starter plan is 100.")
            if amount > 1000:
                raise serializers.ValidationError("Maximum amount for the Starter plan is 1000.")

        elif plan == 'standard':
            if amount <= 1000:
                raise serializers.ValidationError("Minimum amount for the Standard plan must be above 1000.")
            if amount > 10000:
                raise serializers.ValidationError("Maximum amount for the Standard plan is 10000.")

        elif plan == 'advanced':
            if amount <= 10000:
                raise serializers.ValidationError("Minimum amount for the Advanced plan must be above 10000.")
            if amount > 1000000:
                raise serializers.ValidationError("Maximum amount for the Advanced plan is 1000000.")
        
        return data

    # Automatically attach the authenticated user to the payment creation
    # This method is called when creating a new payment
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return Payment.objects.create(**validated_data)



class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'amount_paid', 
            'currency', 'transaction_id', 'status', 
            'verified_by_admin', 'created_at'
        ]



class WithdrawalListSerializer(serializers.ModelSerializer):
    class Meta:
        model= WithdrawalRequest
        fields = '__all__'


class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalRequest
        fields = [
            'user', 'amount', 'bank_name', 'bank_account_number',
            'bank_account_name', 'bank_swift_code', 'bank_routing_number',
            'crypto_currency', 'crypto_address',
        ]
        read_only_fields = ['user']

    def validate(self, data):
        bank_name = data.get('bank_name')
        crypto_currency = data.get('crypto_currency')
        withdrawal_amount = data.get('amount')
        user = self.context.get('user')

        # Fetch the user's balance
        try:
            user_balance = Balance.objects.get(user=user)
        except Balance.DoesNotExist:
            raise serializers.ValidationError("User balance record not found.")

        # Ensure that either bank details or crypto details are provided, but not both
        if not (bank_name or crypto_currency):
            raise serializers.ValidationError("Please provide either bank details or crypto details.")
        
        if bank_name and crypto_currency:
            raise serializers.ValidationError("Please provide only one withdrawal method, not both.")
        
        # Additional validation for bank details
        if bank_name:
            required_bank_fields = [
                'bank_account_number', 'bank_account_name', 
                'bank_swift_code', 'bank_routing_number'
            ]
            for field in required_bank_fields:
                if not data.get(field):
                    raise serializers.ValidationError(f"{field} is required when using bank details.")
        
        # Additional validation for crypto details
        if crypto_currency:
            if not data.get('crypto_address'):
                raise serializers.ValidationError("Crypto address is required when using cryptocurrency.")
        
        # Check if the withdrawal amount is greater than the user's available balance
        if withdrawal_amount > user_balance.balance:
            raise serializers.ValidationError("You cannot withdraw more than your available balance.")

        # Check if the user's balance is $0.00
        if user_balance.balance == 0.00:
            raise serializers.ValidationError("You do not have enough balance to withdraw.")

        return data

    def create(self, validated_data):
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError("User must be provided to create a withdrawal request.")
        
        # Create the withdrawal request
        withdrawal = WithdrawalRequest.objects.create(user=user, **validated_data)
        return withdrawal



class BalanceSerializer(serializers.ModelSerializer):
    user = serializers.EmailField(source='user.email', read_only=True)  
    total_amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Balance
        fields = ['user', 'balance', 'total_amount_paid']



class DailyInterestAccrualSerializer(serializers.ModelSerializer):
    class Meta:
        models= DailyInterestAccrual
        fields= ['user','amount', 'date' ]


