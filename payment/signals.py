from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from .models import Payment, Balance,WithdrawalRequest

@receiver(post_save, sender=Payment)
def update_user_balance(sender, instance, created, update_fields=None, **kwargs):
    """
    Update user's balance only when a payment is marked as completed and verified.
    Triggers on payment creation or status update.
    """
    if instance.status == "completed" and instance.verified_by_admin:
        balance, _ = Balance.objects.get_or_create(user=instance.user)
        balance.update_balance()



@receiver(pre_save, sender=WithdrawalRequest)
def store_previous_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._previous_status = WithdrawalRequest.objects.get(pk=instance.pk).status
        except WithdrawalRequest.DoesNotExist:
            instance._previous_status = None

@receiver(post_save, sender=WithdrawalRequest)
def update_balance_on_withdrawal(sender, instance, created, **kwargs):
    previous = getattr(instance, '_previous_status', None)
    if previous != 'CONFIRMED' and instance.status == 'CONFIRMED':
        balance, _ = Balance.objects.get_or_create(user=instance.user)
        balance.update_balance()

