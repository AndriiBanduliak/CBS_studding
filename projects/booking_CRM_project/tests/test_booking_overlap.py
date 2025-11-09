import datetime as dt
import pytest
from .factories import PropertyFactory, CustomerFactory
from bookings.models import Booking


@pytest.mark.django_db
def test_booking_overlap_validation():
    prop = PropertyFactory()
    cust = CustomerFactory()
    # First booking
    b1 = Booking.objects.create(
        property=prop,
        customer=cust,
        check_in=dt.date(2025, 1, 10),
        check_out=dt.date(2025, 1, 15),
    )

    # Overlapping booking must fail
    with pytest.raises(Exception):
        Booking.objects.create(
            property=prop,
            customer=cust,
            check_in=dt.date(2025, 1, 12),
            check_out=dt.date(2025, 1, 18),
        )

    # Non-overlapping should pass
    b2 = Booking.objects.create(
        property=prop,
        customer=cust,
        check_in=dt.date(2025, 1, 15),
        check_out=dt.date(2025, 1, 17),
    )
    assert b1.id != b2.id

