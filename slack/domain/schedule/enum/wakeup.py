from domain.schedule.schedule import Schedule
from datetime import timedelta
from datetime import datetime as DatetimeObject


class Wakeup:
    CATEGORY = "朝の予定"
    TITLE = "起床"

    @classmethod
    def create(cls, start_datetime: DatetimeObject) -> Schedule:
        end_datetime = start_datetime + timedelta(minutes=15)
        return Schedule(
            category=cls.CATEGORY,
            title=cls.TITLE,
            start=start_datetime,
            end=end_datetime,
        )
