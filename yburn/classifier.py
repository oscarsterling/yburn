"""Classification engine for cron jobs.

Determines whether a cron job is mechanical (replaceable with a local script)
or requires AI reasoning.
"""

import logging

logger = logging.getLogger(__name__)


def classify(cron_job):
    """Classify a cron job as mechanical or reasoning.

    Args:
        cron_job: A CronJob instance from the scanner module.

    Returns:
        A classification result (not yet implemented).
    """
    raise NotImplementedError("Classification engine not yet implemented")
