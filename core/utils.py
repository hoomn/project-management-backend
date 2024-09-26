from django.utils.timesince import timesince
from django.utils.html import avoid_wrapping
from django.utils import timezone, formats
from django.conf import settings

import logging
import os


logger = logging.getLogger(__name__)


def get_timesince(d):
    """
    Take a datetime object and return the time between d and now as a nicely
    formatted string, e.g. `4 days, 6 hours ago`. If the result is `0 minutes`,
    return `a few seconds ago`.
    """
    if not d:
        return ""
    try:
        time_since = timesince(d)
        # Use non-breaking spaces
        if time_since == avoid_wrapping("0 minutes"):
            time_since = "a few seconds"
        return avoid_wrapping(f"{time_since} ago")
    except (ValueError, TypeError):
        return ""


def get_local_time(value):
    """
    Format a datetime according to the US format local time.
    """
    if value in (None, ""):
        return ""
    try:
        local_time = timezone.localtime(value)
        date = formats.date_format(local_time, arg=None)
        time = formats.time_format(local_time, arg=None)
        return f"{ date } { time }"
    except (AttributeError, ValueError):
        return ""


def get_version():
    """
    Read version from the 'version.txt' file located in the base directory of the project.
    """
    path = os.path.join(settings.BASE_DIR, "version.txt")
    try:
        with open(path, "r") as file:
            version = file.read().strip()
        return version or "_._._"

    except Exception as e:
        logger.warning(f"An unexpected error occurred in `get_version()`: {e}")
        return "_._._"


def environment_callback(request):
    """
    Environment callback function to distinguish between
    environments by displaying a label in unfold admin
    """
    version = get_version()

    if settings.DEBUG:
        return [f"Development ({version})", "success"]
    return [f"Production ({version})", "danger"]
