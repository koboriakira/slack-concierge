from domain.schedule.schedule import Schedule, SubTask, Detail
from datetime import timedelta
from datetime import datetime as DatetimeObject
from typing import Optional


class Bathtime:
    CATEGORY = "夜の予定"
    TITLE = "お風呂"
    MARGIN = 45

    @classmethod
    def create(cls, start: DatetimeObject) -> Schedule:
        sub_tasks = []
        sub_tasks.append(SubTask(name="お風呂を準備する"))
        sub_tasks.append(SubTask(name="お風呂に入る"))
        sub_tasks.append(SubTask(name="化粧水をつける"))
        detail = Detail(sub_tasks=sub_tasks)
        end_datetime = start + timedelta(minutes=cls.MARGIN)
        return Schedule(
            category=cls.CATEGORY,
            title=cls.TITLE,
            start=start,
            end=end_datetime,
            detail=detail,
        )
