from django.contrib import admin
from .models import Referral,Contact


class ReferralAdmin(admin.ModelAdmin):
    list_display = ('code','referee', 'referrer','bonus', 'referred_at')
    search_fields = ('referee__user__username', 'referrer__user__username')
    list_filter = ('referred_at',)
    ordering = ('-referred_at',)


admin.site.register(Referral, ReferralAdmin)


class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'body', 'created_on')
    search_fields = ('name', 'email')
    list_filter = ('created_on',)
    ordering = ('-created_on',)

admin.site.register(Contact, ContactAdmin)