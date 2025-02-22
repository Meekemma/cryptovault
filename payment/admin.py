# admin.py
from django.contrib import admin
from .models import WithdrawalRequest, Balance, Payment



class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'bank_name', 'crypto_currency')

admin.site.register(WithdrawalRequest, WithdrawalRequestAdmin)




class BalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'bonus')

admin.site.register(Balance, BalanceAdmin)



@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'plan', 'amount_paid', 'currency', 'status', 'verified_by_admin', 'created_at')
    list_filter = ('status', 'verified_by_admin', 'currency')
    search_fields = ('user__username', 'transaction_id', 'wallet_address')



