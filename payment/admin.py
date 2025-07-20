# admin.py
from django.contrib import admin
from .models import WithdrawalRequest, Balance, Payment,Interest, DailyInterestAccrual



class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'created_at')
    list_editable = ('status',)  # Editable from list view
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'bank_name', 'crypto_currency')
admin.site.register(WithdrawalRequest, WithdrawalRequestAdmin)



class BalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'referral_bonus', 'total_amount_accumulated')
    readonly_fields = ('balance', 'referral_bonus', 'total_amount_accumulated')

    def referral_bonus(self, obj):
        return obj.referral_bonus

    def total_amount_accumulated(self, obj):
        return obj.total_amount_accumulated


admin.site.register(Balance, BalanceAdmin)



@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'plan', 'amount_paid', 'currency', 'status', 'verified_by_admin', 'created_at')
    list_filter = ('status', 'verified_by_admin', 'currency')
    search_fields = ('user__username', 'transaction_id', 'wallet_address')






@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('plan', 'daily_interest_percent')
    list_editable = ('daily_interest_percent',)
    search_fields = ('plan',)
    ordering = ('plan',)


@admin.register(DailyInterestAccrual)
class DailyInterestAccrualAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'date')
    list_filter = ('date',)
    search_fields = ('user__email',)
    ordering = ('-date',)




