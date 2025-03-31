from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'full_name', 'is_active', 'is_staff', 'is_admin', 'is_trainer')
    list_filter = ('is_staff', 'is_admin', 'is_trainer', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'contact_number', 'messenger_account', 'complete_address', 'nationality', 'birthdate', 'gender', 'type_of_membership', 'referral_code')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_admin', 'is_trainer', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'full_name')}
        ),
    )
    search_fields = ('email', 'full_name')
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)
