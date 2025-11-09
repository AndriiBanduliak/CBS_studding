from django.db import models


class RatePlan(models.Model):
    property = models.OneToOneField("properties.Property", on_delete=models.CASCADE, related_name="rate_plan")
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    weekend_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    holiday_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, default="RUB")
    min_nights = models.PositiveIntegerField(default=1)
    max_nights = models.PositiveIntegerField(default=30)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self) -> str:
        return f"RatePlan for {self.property}"


class SeasonalRate(models.Model):
    property = models.ForeignKey("properties.Property", on_delete=models.CASCADE, related_name="seasonal_rates")
    start_date = models.DateField()
    end_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["start_date"]

    def __str__(self) -> str:
        return f"{self.property} {self.start_date}–{self.end_date}"
