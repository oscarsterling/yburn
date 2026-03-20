"""Converter module for replacing mechanical cron jobs with local scripts."""

import logging

logger = logging.getLogger(__name__)


def convert(cron_job, template_dir: str):
    """Convert a mechanical cron job into a local script.

    Args:
        cron_job: A CronJob instance classified as mechanical.
        template_dir: Path to the templates directory.

    Returns:
        Path to the generated script (not yet implemented).
    """
    raise NotImplementedError("Converter not yet implemented")
