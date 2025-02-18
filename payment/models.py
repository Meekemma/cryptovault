# models.py
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.exceptions import ValidationError
from django_coinpayments.models import Payment


class WithdrawalRequest(models.Model):
    CRYPTO_CURRENCY_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('LTC', 'Litecoin'),
        ('BCH', 'Bitcoin Cash'),
        ('USDT', 'Tether'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
    ]


    # User-related fields
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Bank-related fields
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    bank_account_number = models.CharField(max_length=100, blank=True, null=True)
    bank_account_name = models.CharField(max_length=255, blank=True, null=True)
    bank_swift_code = models.CharField(max_length=100, blank=True, null=True)
    bank_routing_number = models.CharField(max_length=100, blank=True, null=True)

    # Crypto-related fields
    crypto_currency = models.CharField(max_length=50, choices=CRYPTO_CURRENCY_CHOICES, blank=True, null=True)  
    crypto_address = models.CharField(max_length=255, blank=True, null=True)

    # Status of the request
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')  # Pending, Approved, Rejected

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Ensure that either bank details or crypto details are provided, but not both
        if not (self.bank_name or self.crypto_currency):
            raise ValidationError('Please provide either bank details or crypto details.')

        if self.bank_name and self.crypto_currency:
            raise ValidationError('Please provide only one withdrawal method, not both.')
    
    def __str__(self):
        return f'Withdrawal request from {self.user.email} - {self.status}'
    
    @property
    def total_amount_withdrawn(self):
        withdrawn_payments = WithdrawalRequest.objects.filter(user=self.user, status="CONFIRMED")
        return sum([withdrawal.amount for withdrawal in withdrawn_payments])



class Balance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='balance')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f'Balance for {self.user.email}: {self.balance}'

    @property
    def total_amount_paid(self):
        paid_payments = Payment.objects.filter(user=self.user, status="PAID")
        return sum([payment.amount_paid for payment in paid_payments])

    @property
    def calculated_balance(self):
        return self.total_amount_paid + self.bonus

    def update_balance(self):
        self.balance = self.calculated_balance
        


    def save(self, *args, **kwargs):
        self.update_balance()
        super().save(*args, **kwargs)



    class Meta:
        verbose_name = 'Balance'
        verbose_name_plural = 'Balances'
