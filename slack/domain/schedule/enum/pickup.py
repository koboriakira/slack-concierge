from domain.schedule.schedule import Schedule
from datetime import timedelta
from datetime import datetime as DatetimeObject


class Pickup:
    CATEGORY = "夜の予定"
    TITLE = "おむかえ"
    MARGIN = 30

    @classmethod
    def create(cls, start: DatetimeObject) -> Schedule:
        end_datetime = start + timedelta(minutes=cls.MARGIN)
        return Schedule(
            category=cls.CATEGORY,
            title=cls.TITLE,
            start=start,
            end=end_datetime,
        )
