from django.db import models
from django.core.exceptions import ValidationError


class Booking(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        CONFIRMED = "confirmed", "Подтверждено"
        CANCELLED = "cancelled", "Отменено"
        CHECKED_IN = "checked_in", "Заселен"
        CHECKED_OUT = "checked_out", "Выселен"

    property = models.ForeignKey("properties.Property", on_delete=models.CASCADE, related_name="bookings")
    customer = models.ForeignKey("customers.Customer", on_delete=models.CASCADE, related_name="bookings")
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONFIRMED)
    source = models.CharField(max_length=50, default="crm")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-check_in", "property_id"]
        indexes = [
            models.Index(fields=["property", "check_in", "check_out"], name="booking_prop_dates"),
            models.Index(fields=["status"], name="booking_status_idx"),
        ]

    def __str__(self) -> str:
        return f"#{self.pk} {self.property} {self.check_in}→{self.check_out}"

    @staticmethod
    def overlaps_exist(property_id: int, check_in, check_out, exclude_id: int | None = None) -> bool:
        qs = Booking.objects.filter(property_id=property_id)
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        # Overlap if: start < other_end AND end > other_start
        qs = qs.filter(check_in__lt=check_out, check_out__gt=check_in)
        qs = qs.exclude(status=Booking.Status.CANCELLED)
        return qs.exists()

    def clean(self):
        if self.check_in >= self.check_out:
            raise ValidationError({"check_out": "check_out must be after check_in"})
        if Booking.overlaps_exist(self.property_id, self.check_in, self.check_out, self.id):
            raise ValidationError("Booking dates overlap with an existing booking for this property")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @staticmethod
    def find_next_available_range(property_id: int, desired_start, nights: int = 1):
        """Return the earliest start date >= desired_start where a block of given nights is free.

        Naive O(n) over existing bookings; optimized by date index.
        """
        from datetime import timedelta
        candidate = desired_start
        end = lambda start: start + timedelta(days=nights)
        while True:
            conflict = (
                Booking.objects.filter(property_id=property_id)
                .filter(check_in__lt=end(candidate), check_out__gt=candidate)
                .exclude(status=Booking.Status.CANCELLED)
                .order_by("check_out")
                .first()
            )
            if not conflict:
                return candidate, end(candidate)
            candidate = max(conflict.check_out, candidate + timedelta(days=1))
