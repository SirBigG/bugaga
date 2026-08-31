from django.contrib.auth.models import User
from django.db import models


class OIDCIdentity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="oidc_identity")
    issuer = models.URLField(max_length=500)
    subject = models.CharField(max_length=255)
    last_synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("issuer", "subject"), name="accounts_oidc_issuer_subject_uniq")]

    def __str__(self):
        return f"{self.issuer}#{self.subject}"
