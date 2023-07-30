from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.models import User


class UserAdmin(BaseUserAdmin):

    ordering = ['email']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('name', 'password')}),
        ('Personal info', {'fields': ('email',)}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active',)}),
        ('Additional information', {'fields': ('last_login',)})
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ['wide'],
            'fields': {'email', 'name', 'password1', 'password2'}
        }),
    )


admin.site.register(User, UserAdmin)
