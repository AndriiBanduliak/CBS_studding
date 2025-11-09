from rest_framework import serializers
from .models import Property, Location, Amenity


class LocationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Location
		fields = ["id", "name", "code", "description", "is_active"]


class PropertySerializer(serializers.ModelSerializer):
	location = LocationSerializer(read_only=True)
	location_id = serializers.PrimaryKeyRelatedField(
		source="location",
		queryset=Location.objects.all(),
		write_only=True,
		allow_null=True,
		required=False,
	)
	calendar_id = serializers.CharField(required=False, allow_blank=True)

	class Meta:
		model = Property
		fields = [
			"id",
			"title",
			"address",
			"description",
			"capacity",
			"color_hex",
			"status",
			"location",
			"location_id",
			"calendar_id",
			"amenities",
		]
		read_only_fields = ["amenities"]
