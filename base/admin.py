from django.contrib import admin
from django.contrib.auth.admin import UserAdmin  as BaseUserAdmin
from .models import User
from .models import *
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin 




admin.site.site_header = "Trexiz Administration"
admin.site.site_title = "Trexiz Admin"
admin.site.index_title = "Trexiz Admin Panel"



class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
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


class UserProfileAdmin(ModelAdmin):
    list_display = ('user_id','user', 'first_name', 'last_name', 'email','gender','phone_number', 'country', 'profile_picture','referral_code', 'date_created', 'date_updated')
    search_fields = ('user__email', 'first_name', 'last_name', 'email')
    list_filter = ( 'date_created', 'date_updated')
admin.site.register(UserProfile, UserProfileAdmin)



class OneTimePasswordAdmin(ModelAdmin):
    list_display = ('user','code')  
    search_fields = ('user__first_name', 'user__last_name', 'code') 

admin.site.register(OneTimePassword, OneTimePasswordAdmin)



# Register the CustomUser model with the CustomUserAdmin





class SubscriptionAdmin(ModelAdmin):
    list_display = ['email', 'subscribed_at', 'is_subscribed']
    list_filter = ['is_subscribed']
    search_fields = ['email']

admin.site.register(Subscription, SubscriptionAdmin)

