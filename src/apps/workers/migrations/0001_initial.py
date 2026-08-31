from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="WorkerState",
            fields=[
                ("name", models.CharField(max_length=100, primary_key=True, serialize=False)),
                ("integer_value", models.BigIntegerField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
