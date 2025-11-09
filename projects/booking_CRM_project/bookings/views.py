from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from .models import Booking
from .serializers import BookingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related("property", "customer").all().order_by("-check_in")
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["property__title", "customer__first_name", "customer__last_name", "customer__email"]
    ordering_fields = ["check_in", "check_out", "status", "guests"]
