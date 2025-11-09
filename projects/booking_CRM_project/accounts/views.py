from django.contrib.auth import authenticate, login, logout, get_user_model
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from properties.models import Property, Location
from bookings.models import Booking
from customers.models import Customer

User = get_user_model()


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def auth_login(request):
	username = request.data.get("username")
	password = request.data.get("password")
	user = authenticate(request, username=username, password=password)
	if not user:
		return Response({"detail": "Invalid credentials"}, status=400)
	login(request, user)
	return Response({"username": user.username})


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def auth_register(request):
	username = request.data.get("username")
	password = request.data.get("password")
	if not username or not password:
		return Response({"detail": "username and password required"}, status=400)
	if User.objects.filter(username=username).exists():
		return Response({"detail": "username already exists"}, status=400)
	user = User.objects.create_user(username=username, password=password)
	login(request, user)
	return Response({"username": user.username})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def auth_logout(request):
	logout(request)
	return Response({"ok": True})


@api_view(["GET"])
@permission_classes([AllowAny])
def current_user(request):
	u = request.user
	if getattr(u, "is_authenticated", False):
		return Response({"username": u.username})
	return Response({"username": None})


@ensure_csrf_cookie
@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def ensure_csrf(request):
	# Возвращает пустой ответ, но устанавливает CSRF-cookie
	return Response({"ok": True})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    # считаем только активные сущности, чтобы мягко удалённые не попадали в KPI
    properties_active = Property.objects.exclude(status=Property.Status.UNAVAILABLE).count()
    locations_active = Location.objects.filter(is_active=True).count()
    return Response({
        "properties": properties_active,
        "bookings": Booking.objects.count(),
        "customers": Customer.objects.count(),
        "locations": locations_active,
    })
