from django.db import models


class WorkerState(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    integer_value = models.BigIntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
