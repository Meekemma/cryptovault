from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from .models import User
from .models import *




class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['id', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'is_verified','get_groups_display', 'auth_provider']
    search_fields = ['id', 'email', 'first_name', 'last_name']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser', 'groups'),
        }),
    )
    ordering = ('email',)

    def get_groups_display(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])

    get_groups_display.short_description = 'Groups'
admin.site.register(User, CustomUserAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id','user', 'first_name', 'last_name', 'email','gender','phone_number', 'country', 'profile_picture','referral_code', 'date_created', 'date_updated')
    search_fields = ('user__email', 'first_name', 'last_name', 'email')
    list_filter = ( 'date_created', 'date_updated')
admin.site.register(UserProfile, UserProfileAdmin)



class OneTimePasswordAdmin(admin.ModelAdmin):
    list_display = ('user','code')  
    search_fields = ('user__first_name', 'user__last_name', 'code') 

admin.site.register(OneTimePassword, OneTimePasswordAdmin)



# Register the CustomUser model with the CustomUserAdmin





class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'is_subscribed']
    list_filter = ['is_subscribed']
    search_fields = ['email']

admin.site.register(Subscription, SubscriptionAdmin)

