from django.contrib import admin
from .models import User
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import ValidationError
from .forms import UserChangeForm, UserCreationForm



class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'full_name', 'is_active' , 'is_admin',)
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password'),
        }),
        ('Personal info', {'fields': ('full_name','image')}),
        ('Permissions', {'fields': ('is_active', 'is_admin')}),
    )

    add_fieldsets = (        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)