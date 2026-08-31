from authlib.integrations.django_client import OAuth
from django.conf import settings

oauth = OAuth()
oauth.register(
    "agromega",
    client_id=settings.OIDC_CLIENT_ID,
    client_secret=settings.OIDC_CLIENT_SECRET,
    server_metadata_url=f"{settings.OIDC_ISSUER}/.well-known/openid-configuration",
    client_kwargs={"scope": settings.OIDC_SCOPES},
)
