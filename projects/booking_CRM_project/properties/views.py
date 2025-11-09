from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Property, Location
from .serializers import PropertySerializer, LocationSerializer
from bookings.models import Booking
from datetime import datetime


class LocationViewSet(viewsets.ModelViewSet):
	queryset = Location.objects.all().order_by("name")
	serializer_class = LocationSerializer
	permission_classes = [IsAuthenticatedOrReadOnly]
	filter_backends = [filters.SearchFilter, filters.OrderingFilter]
	search_fields = ["name", "code"]
	ordering_fields = ["name"]

	def get_queryset(self):
		qs = super().get_queryset()
		# В списке показываем только активные локации (для селектов и т.п.)
		if getattr(self, 'action', None) == 'list':
			return qs.filter(is_active=True)
		return qs

	def destroy(self, request, *args, **kwargs):
		instance = self.get_object()
		if request.query_params.get("hard") == "1":
			instance.delete()
			return Response(status=204)
		instance.is_active = False
		instance.save(update_fields=["is_active"])
		return Response(status=204)


class PropertyViewSet(viewsets.ModelViewSet):
	queryset = Property.objects.select_related("location").all().order_by("title")
	serializer_class = PropertySerializer
	permission_classes = [IsAuthenticatedOrReadOnly]
	filter_backends = [filters.SearchFilter, filters.OrderingFilter]
	search_fields = ["title", "address"]
	ordering_fields = ["title", "capacity", "status"]

	def destroy(self, request, *args, **kwargs):
		instance = self.get_object()
		if request.query_params.get("hard") == "1":
			instance.delete()
			return Response(status=204)
		# мягкое удаление
		instance.status = Property.Status.UNAVAILABLE
		instance.save(update_fields=["status"])
		return Response(status=204)

	@action(detail=True, methods=["get"], url_path="availability")
	def availability(self, request, pk=None):
		"""Return booked ranges and simple availability for a date range.

		Query params: `start=YYYY-MM-DD`, `end=YYYY-MM-DD`
		"""
		prop = self.get_object()
		start_str = request.query_params.get("start")
		end_str = request.query_params.get("end")
		if not start_str or not end_str:
			return Response({"detail": "start and end are required"}, status=400)
		try:
			start = datetime.fromisoformat(start_str).date()
			end = datetime.fromisoformat(end_str).date()
		except ValueError:
			return Response({"detail": "invalid date format"}, status=400)

		booked = (
			Booking.objects.filter(property=prop, check_in__lt=end, check_out__gt=start)
			.exclude(status=Booking.Status.CANCELLED)
			.values("check_in", "check_out", "status")
		)
		return Response({"property": prop.id, "booked": list(booked)})
