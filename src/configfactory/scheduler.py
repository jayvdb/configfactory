import logging
import time

from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings

logger = logging.getLogger(__name__)


def run():
    """Run scheduler."""

    from configfactory.services.backups import clean_backups, create_backup

    logger.info('Starting scheduler')

    # Initialize scheduler
    scheduler = BackgroundScheduler()

    # Add jobs
    scheduler.add_job(
        func=create_backup,
        kwargs={
            'comment': 'Scheduled backup'
        },
        trigger='interval',
        seconds=settings.BACKUPS_INTERVAL
    )

    scheduler.add_job(
        func=clean_backups,
        trigger='interval',
        seconds=settings.BACKUPS_CLEAN_INTERVAL
    )

    # Start scheduler
    scheduler.start()
    try:
        while True:
            time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
