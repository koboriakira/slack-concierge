from domain.schedule.schedule import Schedule, Detail
from datetime import timedelta
from datetime import datetime as DatetimeObject
from typing import Optional


class Breakfast:
    CATEGORY = "朝の予定"
    TITLE = "朝食"
    MARGIN = 30

    @classmethod
    def create(cls, start: DatetimeObject, breakfast_detail: Optional[str] = None) -> Schedule:
        detail = None
        if breakfast_detail is not None:
            detail = Detail(memo=[breakfast_detail])
        end_datetime = start + timedelta(minutes=cls.MARGIN)
        return Schedule(
            category=cls.CATEGORY,
            title=cls.TITLE,
            start=start,
            end=end_datetime,
            detail=detail,
        )
