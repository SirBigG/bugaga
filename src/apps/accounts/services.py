import hashlib

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import transaction

from .models import OIDCIdentity


def _claim_is_true(value):
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes"}
    return value is True


@transaction.atomic
def synchronize_oidc_user(userinfo):
    subject = str(userinfo.get("sub") or "").strip()
    if not subject:
        raise PermissionDenied("OIDC response does not contain a subject.")

    is_staff = _claim_is_true(userinfo.get("is_staff")) or _claim_is_true(userinfo.get("is_superuser"))
    if not is_staff:
        raise PermissionDenied("This account does not have AgroMega staff access.")

    identity = (
        OIDCIdentity.objects.select_related("user")
        .filter(
            issuer=settings.OIDC_ISSUER,
            subject=subject,
        )
        .first()
    )
    if identity is None:
        digest = hashlib.sha256(f"{settings.OIDC_ISSUER}|{subject}".encode()).hexdigest()[:32]
        user = User(username=f"oidc_{digest}")
        user.set_unusable_password()
        user.save()
        identity = OIDCIdentity.objects.create(user=user, issuer=settings.OIDC_ISSUER, subject=subject)
    else:
        user = identity.user

    user.email = str(userinfo.get("email") or "")[:254]
    user.first_name = str(userinfo.get("given_name") or "")[:150]
    user.last_name = str(userinfo.get("family_name") or "")[:150]
    user.is_active = True
    user.is_staff = True
    user.is_superuser = settings.OIDC_SYNC_SUPERUSER and _claim_is_true(userinfo.get("is_superuser"))
    user.save(update_fields=("email", "first_name", "last_name", "is_active", "is_staff", "is_superuser"))
    identity.save(update_fields=("last_synced_at",))
    return user
