from domain.schedule.schedule import Schedule, Detail
from datetime import timedelta
from datetime import datetime as DatetimeObject
from typing import Optional


class Lunch:
    CATEGORY = "昼休み"
    TITLE = "昼食"
    MARGIN = 30

    @classmethod
    def create(cls, start: DatetimeObject, lunch_detail: Optional[str] = None) -> Schedule:
        detail = None
        if lunch_detail is not None:
            detail = Detail(memo=[lunch_detail])
        end_datetime = start + timedelta(minutes=cls.MARGIN)
        return Schedule(
            category=cls.CATEGORY,
            title=cls.TITLE,
            start=start,
            end=end_datetime,
            detail=detail,
        )
