from django.contrib import admin
from .models import Location, Amenity, Property, PropertyAmenity, PropertyPhoto


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    search_fields = ("name", "code")
    list_filter = ("is_active",)


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    search_fields = ("name",)


class PropertyPhotoInline(admin.TabularInline):
    model = PropertyPhoto
    extra = 0


class PropertyAmenityInline(admin.TabularInline):
    model = PropertyAmenity
    extra = 0


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("title", "address", "capacity", "status", "location")
    list_filter = ("status", "location")
    search_fields = ("title", "address")
    inlines = [PropertyAmenityInline, PropertyPhotoInline]
