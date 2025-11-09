import datetime as dt
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from .factories import PropertyFactory, CustomerFactory
from bookings.models import Booking


@pytest.mark.django_db
def test_property_availability_endpoint():
    prop = PropertyFactory()
    cust = CustomerFactory()
    Booking.objects.create(
        property=prop,
        customer=cust,
        check_in=dt.date(2025, 2, 1),
        check_out=dt.date(2025, 2, 5),
    )

    client = APIClient()
    url = f"/api/properties/{prop.id}/availability/?start=2025-02-01&end=2025-02-10"
    res = client.get(url)
    assert res.status_code == 200
    data = res.json()
    assert data["property"] == prop.id
    assert any(b["check_in"] == "2025-02-01" for b in data["booked"])

