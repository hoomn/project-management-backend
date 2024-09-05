from django.utils.timesince import timesince
from django.utils.html import avoid_wrapping
from django.utils import timezone
from django.utils import formats


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
