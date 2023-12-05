import logging
import asyncio

from pytz import utc

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from settings import settings

from tasks import main_task, create_day_news_summary

logger = logging.getLogger('apscheduler.scheduler')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

logger.addHandler(ch)

jobstores = {
    'default': SQLAlchemyJobStore(url=settings.ENGINE)
}

executors = {
    'default': ThreadPoolExecutor(10),
    'processpool': ProcessPoolExecutor(5)
}

job_defaults = {
    'coalesce': False,
    'max_instances': 5
}

scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    timezone=utc,
    **{"daemon": False, "logger": logger}
)
# Delete old jobs from db before added new
jobstores['default'].remove_all_jobs()
scheduler.add_job(main_task, 'interval', minutes=settings.SCHEDULER_INTERVAL, replace_existing=True)
scheduler.add_job(create_day_news_summary, 'cron', hour=19, minute=00, replace_existing=True)

if __name__ == "__main__":
    scheduler.start()
    asyncio.get_event_loop().run_forever()
