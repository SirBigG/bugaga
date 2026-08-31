from django.conf import settings
from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, IntervalSchedule, PeriodicTask


class Command(BaseCommand):
    help = "Create or update disabled-by-default Celery Beat schedules for the legacy workload."

    def add_arguments(self, parser):
        state = parser.add_mutually_exclusive_group()
        state.add_argument(
            "--enable",
            action="store_true",
            help="Enable schedules immediately. Do not use until the legacy scheduler has stopped.",
        )
        state.add_argument(
            "--disable",
            action="store_true",
            help="Disable all managed schedules before rolling back to legacy processes.",
        )

    def _upsert(self, name, defaults, options):
        task = PeriodicTask.objects.filter(name=name).first()
        if task is None:
            task = PeriodicTask(name=name, enabled=False)
        for field, value in defaults.items():
            setattr(task, field, value)
        if options["enable"]:
            task.enabled = True
        elif options["disable"]:
            task.enabled = False
        task.save()
        return task

    def handle(self, *args, **options):
        poll_interval, _ = IntervalSchedule.objects.get_or_create(
            every=settings.TELEGRAM_POLL_INTERVAL_SECONDS,
            period=IntervalSchedule.SECONDS,
        )
        telegram = self._upsert(
            "AgroMega Telegram polling",
            {
                "task": "bugaga.poll_telegram",
                "interval": poll_interval,
                "crontab": None,
                "expire_seconds": max(settings.TELEGRAM_POLL_INTERVAL_SECONDS, 2),
                "description": "Poll Telegram updates and process bot commands without a dedicated service.",
            },
            options,
        )
        interval, _ = IntervalSchedule.objects.get_or_create(
            every=settings.SCHEDULER_INTERVAL,
            period=IntervalSchedule.MINUTES,
        )
        pipeline = self._upsert(
            "AgroMega parsing pipeline",
            {
                "task": "bugaga.run_pipeline",
                "interval": interval,
                "crontab": None,
                "expire_seconds": max(settings.SCHEDULER_INTERVAL * 60, 60),
                "description": "Parse news/adverts, notify subscribers, and classify adverts.",
            },
            options,
        )

        crontab, _ = CrontabSchedule.objects.get_or_create(
            minute="0",
            hour="19",
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
            timezone=settings.BUGAGA_SUMMARY_TIME_ZONE,
        )
        summary = self._upsert(
            "AgroMega daily news summary",
            {
                "task": "bugaga.create_daily_summary",
                "interval": None,
                "crontab": crontab,
                "expire_seconds": 6 * 60 * 60,
                "description": "Create the OpenAI-generated daily news summary at 19:00 Kyiv time.",
            },
            options,
        )
        if options["enable"]:
            state = "enabled"
        elif options["disable"]:
            state = "disabled"
        else:
            state = "left in their existing enabled/disabled state"
        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {telegram.name}, {pipeline.name}, and {summary.name}; schedules were {state}."
            )
        )
