from datetime import date, datetime
from typing import Final
from zoneinfo import ZoneInfo

from arttrip.application.util.utc import to_utc

SERVICE_TIMEZONE: Final = ZoneInfo("Asia/Seoul")


def to_service_date(now: datetime) -> date:
    return to_utc(now).astimezone(SERVICE_TIMEZONE).date()
