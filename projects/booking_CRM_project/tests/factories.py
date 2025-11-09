import factory
from faker import Faker

fake = Faker()

class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "properties.Location"

    name = factory.LazyAttribute(lambda _: fake.city())
    code = factory.LazyAttribute(lambda _: fake.pystr(min_chars=3, max_chars=5))


class PropertyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "properties.Property"

    title = factory.LazyAttribute(lambda _: fake.street_address())
    address = factory.LazyAttribute(lambda _: fake.address())
    capacity = 2
    location = factory.SubFactory(LocationFactory)


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "customers.Customer"

    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    email = factory.LazyAttribute(lambda _: fake.unique.email())


class BookingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "bookings.Booking"

    property = factory.SubFactory(PropertyFactory)
    customer = factory.SubFactory(CustomerFactory)
    check_in = factory.Faker("date_object")
    check_out = factory.LazyAttribute(lambda o: fake.date_object())
    guests = 1

