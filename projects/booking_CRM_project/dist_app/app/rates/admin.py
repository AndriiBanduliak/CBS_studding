from django.contrib import admin
from .models import RatePlan, SeasonalRate


@admin.register(RatePlan)
class RatePlanAdmin(admin.ModelAdmin):
    list_display = ("property", "base_price", "weekend_price", "holiday_price", "currency")


@admin.register(SeasonalRate)
class SeasonalRateAdmin(admin.ModelAdmin):
    list_display = ("property", "start_date", "end_date", "price")
    ordering = ("start_date",)
