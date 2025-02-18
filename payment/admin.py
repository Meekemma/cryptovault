# admin.py
from django.contrib import admin
from .models import WithdrawalRequest,Balance

class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'bank_name', 'crypto_currency')

admin.site.register(WithdrawalRequest, WithdrawalRequestAdmin)


class BalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'bonus')

admin.site.register(Balance, BalanceAdmin)
