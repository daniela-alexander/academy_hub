from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "Academy Hub",
            {
                "fields": (
                    "avatar",
                    "city",
                    "bio",
                    "phone",
                    "is_verified",
                )
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at")