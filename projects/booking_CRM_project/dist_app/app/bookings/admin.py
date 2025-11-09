from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "property", "customer", "check_in", "check_out", "status")
    list_filter = ("status", "property")
    search_fields = ("id", "customer__first_name", "customer__last_name", "property__title")
