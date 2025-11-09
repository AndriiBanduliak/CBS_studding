import os
import json
import urllib.parse
from datetime import datetime, timedelta
import requests
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from .models import CalendarAccount, CalendarSyncState, CalendarSubscription, CalendarEventLink, WebhookEvent
from bookings.models import Booking
from customers.models import Customer
from properties.models import Property
from django.conf import settings
import uuid
from icalendar import Calendar
import io
from .models import CalendarAccount, CalendarSyncState


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def google_oauth_start(request):
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/integrations/google/callback/")
    scope = "https://www.googleapis.com/auth/calendar.events https://www.googleapis.com/auth/userinfo.email openid"
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
        "scope": scope,
        "state": "",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return Response({"auth_url": url})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def google_oauth_callback(request):
    code = request.query_params.get("code")
    if not code:
        return Response({"detail": "missing code"}, status=400)

    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/integrations/google/callback/")

    token_resp = requests.post("https://oauth2.googleapis.com/token", data={
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    })
    if token_resp.status_code != 200:
        return Response({"detail": "token exchange failed", "raw": token_resp.text}, status=400)

    payload = token_resp.json()
    access_token = payload.get("access_token", "")
    refresh_token = payload.get("refresh_token", "")
    expires_in = payload.get("expires_in", 3600)
    token_expiry = datetime.utcnow() + timedelta(seconds=int(expires_in))
    id_token = payload.get("id_token", "")

    email = None
    try:
        # Decode id_token payload segment
        parts = id_token.split(".")
        if len(parts) >= 2:
            data = json.loads(urllib.parse.unquote_plus(parts[1] + "=="))
            email = data.get("email")
    except Exception:
        pass

    acct, _ = CalendarAccount.objects.get_or_create(user=request.user, provider=CalendarAccount.PROVIDER_GOOGLE, email=email or "")
    acct.access_token = access_token
    if refresh_token:
        acct.refresh_token = refresh_token
    acct.token_expiry = token_expiry
    acct.scopes = "calendar.events,userinfo.email,openid"
    acct.save()

    return Response({"ok": True, "email": acct.email})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def google_list_calendars(request):
    try:
        acct = CalendarAccount.objects.filter(user=request.user, provider=CalendarAccount.PROVIDER_GOOGLE).latest("updated_at")
    except CalendarAccount.DoesNotExist:
        return Response({"detail": "no google account connected"}, status=404)

    headers = {"Authorization": f"Bearer {acct.access_token}"}
    resp = requests.get("https://www.googleapis.com/calendar/v3/users/me/calendarList", headers=headers)
    if resp.status_code != 200:
        return Response({"detail": "failed", "raw": resp.text}, status=resp.status_code)
    return Response(resp.json())

@csrf_exempt
@api_view(["POST"])  # Google sends POST notifications
@permission_classes([])
@authentication_classes([])
def google_webhook(request):
    """Webhook endpoint for Google push notifications.

    In dev we accept all requests. In prod, validate channel token/header
    against settings.GOOGLE_WEBHOOK_VERIFICATION_TOKEN and map resourceId to
    a known subscription. Here we simply acknowledge receipt.
    """
    token_header = request.headers.get("X-Goog-Channel-Token", "")
    expected = getattr(settings, "GOOGLE_WEBHOOK_VERIFICATION_TOKEN", "")
    if expected and token_header != expected:
        return Response({"detail": "forbidden"}, status=403)

    resource_id = request.headers.get("X-Goog-Resource-Id", "")
    message_num = request.headers.get("X-Goog-Message-Number", "")
    # Idempotency key: provider+resource+message_num
    idem_key = f"google:{resource_id}:{message_num}"
    created = False
    try:
        WebhookEvent.objects.get(external_id=idem_key)
    except WebhookEvent.DoesNotExist:
        WebhookEvent.objects.create(provider="google", external_id=idem_key)
        created = True
    # Mark subscription touched (optional)
    CalendarSubscription.objects.filter(resource_id=resource_id).update(active=True)
    return Response({"ok": True, "processed": created})

# Placeholder sync function — to be wired into Celery later.
def _extract_dates(google_event: dict):
    start = google_event.get("start", {})
    end = google_event.get("end", {})
    # Prefer all-day date, else take dateTime and convert to date
    from datetime import datetime
    def to_date(v):
        if not v:
            return None
        if v.get("date"):
            return datetime.fromisoformat(v["date"]) .date()
        if v.get("dateTime"):
            # Strip timezone if present
            return datetime.fromisoformat(v["dateTime"].replace("Z", "+00:00")).date()
        return None
    return to_date(start), to_date(end)


def upsert_events_deduplicated(account: CalendarAccount, calendar_id: str, events: list[dict]) -> None:
    """Insert/update events with deduplication by iCalUID.

    - Resolves `Property` by `Property.calendar_id` matching provided calendar_id
    - Chooses customer from first attendee/organizer email, otherwise creates/uses "Calendar Guest"
    - Creates or updates `Booking` via `CalendarEventLink` keyed by event `iCalUID`
    - Skips cancelled events
    """
    try:
        prop = Property.objects.get(calendar_id=calendar_id)
    except Property.DoesNotExist:
        return

    for ev in events:
        if ev.get("status") == "cancelled":
            ical = ev.get("iCalUID") or ev.get("id")
            if ical:
                CalendarEventLink.objects.filter(ical_uid=ical).delete()
            continue

        ical_uid = ev.get("iCalUID") or ev.get("id")
        if not ical_uid:
            continue

        check_in, check_out = _extract_dates(ev)
        if not check_in or not check_out:
            continue

        # Resolve customer
        email = None
        if ev.get("attendees") and isinstance(ev["attendees"], list) and ev["attendees"]:
            email = ev["attendees"][0].get("email")
        if not email:
            email = (ev.get("creator") or {}).get("email") or (ev.get("organizer") or {}).get("email")
        if email:
            customer, _ = Customer.objects.get_or_create(email=email, defaults={"first_name": email.split("@")[0]})
        else:
            customer, _ = Customer.objects.get_or_create(email="calendar-guest@example.invalid", defaults={"first_name": "Calendar", "last_name": "Guest"})

        link = CalendarEventLink.objects.filter(ical_uid=ical_uid).first()
        if link and link.booking:
            b = link.booking
            b.property = prop
            b.customer = customer
            b.check_in = check_in
            b.check_out = check_out
            b.source = "google"
            b.save()
        else:
            b = Booking.objects.create(
                property=prop,
                customer=customer,
                check_in=check_in,
                check_out=check_out,
                guests=1,
                status=Booking.Status.CONFIRMED,
                source="google",
            )
            CalendarEventLink.objects.update_or_create(
                ical_uid=ical_uid,
                defaults={"provider": CalendarEventLink.PROVIDER_GOOGLE, "calendar_id": calendar_id, "booking": b},
            )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def google_watch_start(request):
    """Start watching a particular calendar's events."""
    calendar_id = request.data.get("calendar_id")
    if not calendar_id:
        return Response({"detail": "calendar_id required"}, status=400)

    try:
        acct = CalendarAccount.objects.filter(user=request.user, provider=CalendarAccount.PROVIDER_GOOGLE).latest("updated_at")
    except CalendarAccount.DoesNotExist:
        return Response({"detail": "no google account connected"}, status=404)

    channel_id = str(uuid.uuid4())
    token = getattr(settings, "GOOGLE_WEBHOOK_VERIFICATION_TOKEN", "")
    callback = request.build_absolute_uri("/api/integrations/google/webhook/")
    headers = {"Authorization": f"Bearer {acct.access_token}", "Content-Type": "application/json"}
    data = {
        "id": channel_id,
        "type": "web_hook",
        "address": callback,
        "token": token,
    }
    resp = requests.post(
        f"https://www.googleapis.com/calendar/v3/calendars/{urllib.parse.quote(calendar_id)}/events/watch",
        headers=headers,
        json=data,
    )
    if resp.status_code != 200:
        return Response({"detail": "watch failed", "raw": resp.text}, status=resp.status_code)

    payload = resp.json()
    sub = CalendarSubscription.objects.create(
        account=acct,
        calendar_id=calendar_id,
        channel_id=payload.get("id", channel_id),
        resource_id=payload.get("resourceId", ""),
        token=token,
        active=True,
    )
    return Response({"ok": True, "channel_id": sub.channel_id, "resource_id": sub.resource_id})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def google_watch_stop(request):
    """Stop a previously created watch channel."""
    channel_id = request.data.get("channel_id")
    resource_id = request.data.get("resource_id")
    if not channel_id or not resource_id:
        return Response({"detail": "channel_id and resource_id required"}, status=400)

    try:
        acct = CalendarAccount.objects.filter(user=request.user, provider=CalendarAccount.PROVIDER_GOOGLE).latest("updated_at")
    except CalendarAccount.DoesNotExist:
        return Response({"detail": "no google account connected"}, status=404)

    headers = {"Authorization": f"Bearer {acct.access_token}", "Content-Type": "application/json"}
    data = {"id": channel_id, "resourceId": resource_id}
    resp = requests.post("https://www.googleapis.com/calendar/v3/channels/stop", headers=headers, json=data)
    CalendarSubscription.objects.filter(channel_id=channel_id, resource_id=resource_id).update(active=False)
    if resp.status_code not in (200, 204):
        return Response({"detail": "stop failed", "raw": resp.text}, status=resp.status_code)
    return Response({"ok": True})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def google_sync_now(request):
    """Manual one-shot sync for a calendar: first full load or delta by sync_token."""
    calendar_id = request.data.get("calendar_id")
    if not calendar_id:
        return Response({"detail": "calendar_id required"}, status=400)

    try:
        acct = CalendarAccount.objects.filter(user=request.user, provider=CalendarAccount.PROVIDER_GOOGLE).latest("updated_at")
    except CalendarAccount.DoesNotExist:
        return Response({"detail": "no google account connected"}, status=404)

    state, _ = CalendarSyncState.objects.get_or_create(account=acct, calendar_id=calendar_id)
    headers = {"Authorization": f"Bearer {acct.access_token}"}
    params = {"singleEvents": True, "maxResults": 2500}
    if state.sync_token:
        params["syncToken"] = state.sync_token
    else:
        params["timeMin"] = datetime.utcnow().isoformat() + "Z"

    resp = requests.get(
        f"https://www.googleapis.com/calendar/v3/calendars/{urllib.parse.quote(calendar_id)}/events",
        headers=headers,
        params=params,
    )
    if resp.status_code != 200:
        return Response({"detail": "events fetch failed", "raw": resp.text}, status=resp.status_code)
    data = resp.json()
    items = data.get("items", [])
    upsert_events_deduplicated(acct, calendar_id, items)
    new_token = data.get("nextSyncToken")
    if new_token:
        state.sync_token = new_token
        state.last_synced_at = datetime.utcnow()
        state.save()
    return Response({"ok": True, "received": len(items), "has_next": bool(new_token)})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def channels_import_ical(request):
    """Import bookings from iCal feed for a property with dedup by UID.

    Body: { "property_id": number, "ical_url": string }
    """
    property_id = request.data.get("property_id")
    ical_url = request.data.get("ical_url")
    if not property_id or not ical_url:
        return Response({"detail": "property_id and ical_url required"}, status=400)

    from properties.models import Property
    from customers.models import Customer
    try:
        prop = Property.objects.get(id=property_id)
    except Property.DoesNotExist:
        return Response({"detail": "property not found"}, status=404)

    resp = requests.get(ical_url, timeout=20)
    if resp.status_code != 200:
        return Response({"detail": "failed to fetch ical", "status": resp.status_code}, status=400)
    try:
        cal = Calendar.from_ical(resp.content)
    except Exception:
        # Some feeds are text with encoding quirks
        cal = Calendar.from_ical(io.BytesIO(resp.content).read())

    imported = 0
    for component in cal.walk():
        if component.name != "VEVENT":
            continue
        uid = str(component.get("uid")) if component.get("uid") else None
        dtstart = component.get("dtstart")
        dtend = component.get("dtend")
        if not uid or not dtstart or not dtend:
            continue
        # Normalize to dates
        s = dtstart.dt.date() if hasattr(dtstart.dt, "date") else dtstart.dt
        e = dtend.dt.date() if hasattr(dtend.dt, "date") else dtend.dt
        # Resolve/ensure customer placeholder
        customer, _ = Customer.objects.get_or_create(email="ical-guest@example.invalid", defaults={"first_name": "iCal", "last_name": "Guest"})
        link = CalendarEventLink.objects.filter(ical_uid=uid).first()
        if link and link.booking:
            b = link.booking
            b.property = prop
            b.customer = customer
            b.check_in = s
            b.check_out = e
            b.source = "ical"
            b.save()
        else:
            b = Booking.objects.create(property=prop, customer=customer, check_in=s, check_out=e, guests=1, source="ical")
            CalendarEventLink.objects.update_or_create(
                ical_uid=uid,
                defaults={"provider": "ical", "calendar_id": prop.calendar_id or "ical", "booking": b},
            )
        imported += 1
    return Response({"ok": True, "imported": imported})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def payments_list_providers(request):
    """Placeholder: list supported payment providers and connection status."""
    providers = [
        {"key": "stripe", "name": "Stripe", "connected": False},
        {"key": "liqpay", "name": "LiqPay", "connected": False},
        {"key": "wayforpay", "name": "WayForPay", "connected": False},
    ]
    return Response({"providers": providers})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def payments_create_intent(request):
    """Create payment intent (Stripe skeleton). Body: {amount_cents, currency}"""
    amount = int(request.data.get("amount_cents", 0))
    currency = (request.data.get("currency") or "usd").lower()
    if amount <= 0:
        return Response({"detail": "amount_cents must be > 0"}, status=400)
    sk = getattr(settings, "STRIPE_SECRET_KEY", "")
    if not sk:
        # Dev fallback
        return Response({"id": "pi_test", "client_secret": "test_secret"})
    import stripe
    stripe.api_key = sk
    pi = stripe.PaymentIntent.create(amount=amount, currency=currency, automatic_payment_methods={"enabled": True})
    return Response({"id": pi.id, "client_secret": pi.client_secret})


@csrf_exempt
@api_view(["POST"])  # Stripe webhook
@permission_classes([])
@authentication_classes([])
def payments_webhook(request):
    payload = request.body
    sig = request.headers.get("Stripe-Signature", "")
    secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")
    if not secret:
        return Response({"ok": True})
    import stripe
    try:
        event = stripe.Webhook.construct_event(payload=payload, sig_header=sig, secret=secret)
    except Exception:
        return Response(status=400)
    # TODO: handle events (payment_intent.succeeded, etc.)
    return Response({"ok": True, "type": event.get("type")})
