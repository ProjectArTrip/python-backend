from datetime import datetime, timedelta

from arttrip.application.util.utc import to_utc


def get_recent_exhibit_retention_start(now: datetime, *, days: int) -> datetime:
    return to_utc(now) - timedelta(days=days)
