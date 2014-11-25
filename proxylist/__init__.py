from dateutil.parser import parse as _parse
from datetime import datetime
from django.conf import settings


def now():
    now = datetime.now
    try:
        from django.utils.timezone import now
    except ImportError:
        pass
    return now()


def parse(val):
    if settings.USE_TZ:
        return _parse(val)
    return _parse(val).replace(tzinfo=None)

import signals
