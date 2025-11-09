from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "property",
            "customer",
            "check_in",
            "check_out",
            "guests",
            "status",
            "source",
        ]

    def validate(self, attrs):
        check_in = attrs.get("check_in", getattr(self.instance, "check_in", None))
        check_out = attrs.get("check_out", getattr(self.instance, "check_out", None))
        property_id = attrs.get("property", getattr(self.instance, "property_id", None))
        if check_in and check_out and check_in >= check_out:
            raise serializers.ValidationError({"detail": "Дата выезда должна быть позже даты заезда"})
        # overlap check
        instance_id = getattr(self.instance, "id", None)
        if property_id and check_in and check_out and Booking.overlaps_exist(property_id.id if hasattr(property_id, 'id') else property_id, check_in, check_out, instance_id):
            raise serializers.ValidationError({"detail": "Эти даты уже заняты для выбранного объекта"})
        return attrs

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"detail": "; ".join(sum(e.message_dict.values(), []))})

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"detail": "; ".join(sum(e.message_dict.values(), []))})


