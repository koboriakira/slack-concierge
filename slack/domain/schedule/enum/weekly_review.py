from domain.schedule.schedule import Schedule
from datetime import timedelta
from datetime import datetime as DatetimeObject


class WeeklyReview:
    CATEGORY = "プライベート"
    TITLE = "週次レビュー"
    MARGIN = 120

    @classmethod
    def create(cls, start: DatetimeObject) -> Schedule:
        end_datetime = start + timedelta(minutes=cls.MARGIN)
        return Schedule(
            category=cls.CATEGORY,
            title=cls.TITLE,
            start=start,
            end=end_datetime,
        )
