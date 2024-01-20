from domain.schedule.schedule import Schedule, SubTask, Detail
from datetime import timedelta
from datetime import datetime as DatetimeObject
from typing import Optional


class GoToKindergarten:
    CATEGORY = "朝の予定"
    TITLE = "登園"
    MARGIN = 30

    @classmethod
    def create(cls, start: DatetimeObject) -> Schedule:
        sub_tasks = []
        sub_tasks.append(SubTask(name="連絡帳を送る"))
        sub_tasks.append(SubTask(name="登園バッグを準備する"))
        sub_tasks.append(SubTask(name="登園"))
        detail = Detail(sub_tasks=sub_tasks)
        end_datetime = start + timedelta(minutes=cls.MARGIN)
        return Schedule(
            category=cls.CATEGORY,
            title=cls.TITLE,
            start=start,
            end=end_datetime,
            detail=detail,
        )
