from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone", "is_vip")
    search_fields = ("first_name", "last_name", "email", "phone")
    list_filter = ("is_vip",)
