from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=50, blank=True, null=True, help_text="Условный код/зона")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Amenity(models.Model):
    name = models.CharField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Property(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Доступен"
        BOOKED = "booked", "Забронирован"
        CLEANING = "cleaning", "На уборке"
        UNAVAILABLE = "unavailable", "Недоступен"

    title = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(default=1)
    color_hex = models.CharField(max_length=7, default="#4f46e5", help_text="#RRGGBB")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name="properties")
    amenities = models.ManyToManyField(Amenity, through="PropertyAmenity", related_name="properties", blank=True)
    calendar_id = models.CharField(max_length=255, blank=True, help_text="External calendar id (e.g., Google)")

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class PropertyAmenity(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("property", "amenity")


class PropertyPhoto(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="properties/photos/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
