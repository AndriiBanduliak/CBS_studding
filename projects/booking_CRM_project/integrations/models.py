from django.db import models
from django.contrib.auth import get_user_model
from bookings.models import Booking

User = get_user_model()


class CalendarAccount(models.Model):
    PROVIDER_GOOGLE = "google"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="calendar_accounts")
    provider = models.CharField(max_length=20, default=PROVIDER_GOOGLE)
    email = models.EmailField(blank=True)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)
    scopes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "provider", "email")

    def __str__(self) -> str:
        return f"{self.provider}:{self.email or self.user_id}"

class CalendarSyncState(models.Model):
    """Keeps track of incremental sync state for a calendar.

    For Google Calendar we store `sync_token` returned by events.list to perform
    delta syncs and avoid full scans. `last_synced_at` is informational.
    """

    account = models.ForeignKey(CalendarAccount, on_delete=models.CASCADE, related_name="sync_states")
    calendar_id = models.CharField(max_length=255)
    provider = models.CharField(max_length=20, default=CalendarAccount.PROVIDER_GOOGLE)
    sync_token = models.TextField(blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("account", "calendar_id", "provider")

    def __str__(self) -> str:
        return f"sync:{self.provider}:{self.calendar_id}"


class CalendarSubscription(models.Model):
    """Google watch channel subscription metadata.

    Stores identifiers needed to stop a channel and correlate webhook events.
    """

    account = models.ForeignKey(CalendarAccount, on_delete=models.CASCADE, related_name="subscriptions")
    calendar_id = models.CharField(max_length=255)
    provider = models.CharField(max_length=20, default=CalendarAccount.PROVIDER_GOOGLE)
    channel_id = models.CharField(max_length=255)  # X-Goog-Channel-Id we generate
    resource_id = models.CharField(max_length=255)  # X-Goog-Resource-Id from Google
    token = models.CharField(max_length=255, blank=True)  # verification token we sent
    expiration = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["resource_id"]),
            models.Index(fields=["channel_id"]),
        ]
        unique_together = ("account", "calendar_id", "provider", "channel_id")

    def __str__(self) -> str:
        return f"sub:{self.provider}:{self.calendar_id}:{self.channel_id}"


class CalendarEventLink(models.Model):
    """Link between external calendar event and internal Booking."""

    PROVIDER_GOOGLE = CalendarAccount.PROVIDER_GOOGLE

    provider = models.CharField(max_length=20, default=PROVIDER_GOOGLE)
    ical_uid = models.CharField(max_length=255, unique=True)
    calendar_id = models.CharField(max_length=255)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="calendar_link")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"link:{self.provider}:{self.ical_uid}→{self.booking_id}"


class WebhookEvent(models.Model):
    """Idempotency for inbound webhooks (provider + external id)."""

    provider = models.CharField(max_length=50)
    external_id = models.CharField(max_length=255, unique=True)
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"webhook:{self.provider}:{self.external_id}"
