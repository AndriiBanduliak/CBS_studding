from datetime import datetime, timedelta
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from bookings.models import Booking
from properties.models import Property

def _parse_date(s: str):
    return datetime.fromisoformat(s).date()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def occupancy_report(request):
    """Return simple occupancy summary per property for a date range.

    Query: start=YYYY-MM-DD, end=YYYY-MM-DD
    """
    start_q = request.query_params.get("start")
    end_q = request.query_params.get("end")
    if not start_q or not end_q:
        return Response({"detail": "start and end are required"}, status=400)
    try:
        start = _parse_date(start_q)
        end = _parse_date(end_q)
    except Exception:
        return Response({"detail": "invalid date format"}, status=400)

    days_total = max(0, (end - start).days)
    data = []
    for prop in Property.objects.all().order_by("title"):
        qs = (
            Booking.objects.filter(property=prop, check_in__lt=end, check_out__gt=start)
            .exclude(status=Booking.Status.CANCELLED)
            .values("check_in", "check_out")
        )
        booked_days = 0
        for b in qs:
            s = max(b["check_in"], start)
            e = min(b["check_out"], end)
            booked_days += max(0, (e - s).days)
        occ = (booked_days / days_total) if days_total else 0
        data.append({
            "property_id": prop.id,
            "property": prop.title,
            "booked_days": booked_days,
            "days_total": days_total,
            "occupancy": round(occ, 4),
        })
    return Response({"start": str(start), "end": str(end), "items": data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def bookings_csv_export(request):
    """Export bookings as CSV for a date range (overlaps included)."""
    start_q = request.query_params.get("start")
    end_q = request.query_params.get("end")
    if not start_q or not end_q:
        return Response({"detail": "start and end are required"}, status=400)
    try:
        start = _parse_date(start_q)
        end = _parse_date(end_q)
    except Exception:
        return Response({"detail": "invalid date format"}, status=400)

    qs = (
        Booking.objects.select_related("property", "customer")
        .filter(check_in__lt=end, check_out__gt=start)
        .order_by("property_id", "check_in")
    )
    rows = [
        [
            "id",
            "property",
            "customer",
            "check_in",
            "check_out",
            "status",
            "guests",
            "source",
        ]
    ]
    for b in qs:
        rows.append([
            b.id,
            b.property.title,
            str(b.customer),
            str(b.check_in),
            str(b.check_out),
            b.status,
            b.guests,
            b.source,
        ])
    # Serialize to CSV
    import csv
    resp = HttpResponse(content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = "attachment; filename=bookings.csv"
    writer = csv.writer(resp)
    for r in rows:
        writer.writerow(r)
    return resp
