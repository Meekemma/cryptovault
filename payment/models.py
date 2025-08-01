import uuid
from django.db import models
from decimal import Decimal
from django.utils import timezone
from base.models import UserProfile
from management.models import Referral
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class Payment(models.Model):
    PAYMENT_STATUS = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]


    PLAN_CHOICES = [
        ('starter', 'Starter'),
        ('standard', 'Standard'),
        ('advanced', 'Advanced'),  
    ]

    CURRENCY_CHOICES = [
        ('BTC', 'BTC'),
        ('XRP', 'XRP'),
        ('USDT', 'USDT'),
        ('USD', 'USD'),
    ]



    plan = models.CharField(max_length=50, choices=PLAN_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=18, decimal_places=8)
    currency = models.CharField(max_length=10, default="BTC", choices=CURRENCY_CHOICES)  
    transaction_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default="pending")
    verified_by_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.amount_paid} {self.currency} ({self.status})"





class WithdrawalRequest(models.Model):
    CRYPTO_CURRENCY_CHOICES = [
        ('BTC', 'BTC'),
        ('XRP', 'XRP'),
        ('USDT', 'USDT'),
        ('USD', 'USD'),
    ]


    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
    ]

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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')  

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    def clean(self):
        has_bank_details = any([self.bank_name, self.bank_account_number, self.bank_account_name])
        has_crypto_details = bool(self.crypto_currency and self.crypto_address)

        if not has_bank_details and not has_crypto_details:
            raise ValidationError('Please provide either bank details or crypto details.')

        if has_bank_details and has_crypto_details:
            raise ValidationError('Please provide only one withdrawal method, not both.')

    def __str__(self):
        return f'Withdrawal request from {self.user.email} - {self.status}'



    @property
    def total_amount_withdrawn(self):
        total = WithdrawalRequest.objects.filter(
            user=self.user,
            status="CONFIRMED"
        ).aggregate(models.Sum('amount'))['amount__sum']
        return total or Decimal('0.00')
    


class Balance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='balance')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f'Balance for {self.user.email}: {self.balance}'

    @property
    def total_amount_accumulated(self):
        total = Payment.objects.filter(
            user=self.user, 
            status="completed", 
            verified_by_admin=True
        ).aggregate(total=models.Sum('amount_paid'))['total']

        return Decimal(total) if total is not None else Decimal("0.00")

    @property
    def referral_bonus(self):
        try:
            profile = self.user.userprofile 
        except UserProfile.DoesNotExist:
            return Decimal("0.00")
        total_bonus = Referral.get_referral_bonus(profile)
        return Decimal(total_bonus)

    def update_balance(self):
        payments_total = self.total_amount_accumulated
        referral_total = self.referral_bonus

        withdrawals_total = WithdrawalRequest.objects.filter(
            user=self.user,
            status="CONFIRMED"
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

        self.balance = (payments_total + referral_total) - withdrawals_total
        self.save(update_fields=['balance'])






class Interest(models.Model):
    PLAN_CHOICES = [
        ('starter', 'Starter'),
        ('standard', 'Standard'),
        ('advanced', 'Advanced'),  
    ]

    plan = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    daily_interest_percent = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.plan} - {self.daily_interest_percent}% daily interest"
    


    
class DailyInterestAccrual(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_interests')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='daily_accruals')
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=18, decimal_places=8)

    class Meta:
        unique_together = ('user', 'payment', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.email} - {self.amount} interest on {self.date}"
