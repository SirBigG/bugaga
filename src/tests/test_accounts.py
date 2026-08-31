from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory

from apps.accounts.models import OIDCIdentity
from apps.accounts.services import synchronize_oidc_user
from apps.accounts.views import _safe_next


@pytest.mark.django_db
def test_staff_claim_creates_local_oidc_user():
    user = synchronize_oidc_user(
        {
            "sub": "agromega-user-42",
            "email": "staff@example.com",
            "given_name": "Staff",
            "family_name": "Member",
            "is_staff": True,
        }
    )

    assert user.is_staff is True
    assert user.is_superuser is False
    assert user.has_usable_password() is False
    assert OIDCIdentity.objects.get(user=user).subject == "agromega-user-42"


@pytest.mark.django_db
def test_non_staff_oidc_user_is_rejected():
    with pytest.raises(PermissionDenied):
        synchronize_oidc_user({"sub": "regular-user", "is_staff": False})

    assert User.objects.count() == 0


@pytest.mark.django_db
def test_admin_redirects_anonymous_user_to_oidc(client):
    response = client.get("/admin/login/", {"next": "/admin/"})

    assert response.status_code == 302
    assert response.url.startswith("/oidc/login/")


def test_oidc_next_redirect_is_limited_to_this_service():
    request = RequestFactory().get("/oidc/login/", secure=True, HTTP_HOST="testserver")

    assert _safe_next(request, "/admin/") == "/admin/"
    assert _safe_next(request, "https://evil.example/admin/") == "/admin/"


@pytest.mark.django_db
def test_oidc_callback_logs_in_staff_user(client):
    token = {
        "id_token": "signed-id-token",
        "userinfo": {
            "sub": "staff-subject",
            "email": "staff@example.com",
        },
    }
    endpoint_userinfo = {
        "sub": "staff-subject",
        "email": "staff@example.com",
        "is_staff": True,
    }
    with (
        patch("apps.accounts.views.oauth.agromega.authorize_access_token", return_value=token),
        patch("apps.accounts.views.oauth.agromega.userinfo", return_value=endpoint_userinfo) as userinfo,
    ):
        response = client.get("/oidc/callback/", {"code": "code", "state": "state"})

    assert response.status_code == 302
    assert response.url == "/admin/"
    userinfo.assert_called_once_with(token=token)
    assert client.session["_auth_user_id"] == str(User.objects.get(email="staff@example.com").pk)


@pytest.mark.django_db
def test_oidc_callback_rejects_non_staff_user(client):
    token = {"userinfo": {"sub": "regular-subject", "is_staff": False}}
    with (
        patch("apps.accounts.views.oauth.agromega.authorize_access_token", return_value=token),
        patch(
            "apps.accounts.views.oauth.agromega.userinfo",
            return_value={"sub": "regular-subject", "is_staff": False},
        ),
    ):
        response = client.get("/oidc/callback/", {"code": "code", "state": "state"})

    assert response.status_code == 403
    assert User.objects.count() == 0
