from domain.schedule.schedule import Schedule, SubTask, Detail
from datetime import timedelta
from datetime import datetime as DatetimeObject
from typing import Optional


class Bedtime:
    CATEGORY = "夜の予定"
    TITLE = "寝かしつけ"
    MARGIN = 90

    @classmethod
    def create(cls, start: DatetimeObject) -> Schedule:
        sub_tasks = []
        sub_tasks.append(SubTask(name="歯磨き"))
        sub_tasks.append(SubTask(name="居間を片付ける"))
        sub_tasks.append(SubTask(name="登園バッグの準備"))
        sub_tasks.append(SubTask(name="連絡帳を書く"))
        detail = Detail(sub_tasks=sub_tasks)
        end_datetime = start + timedelta(minutes=cls.MARGIN)
        return Schedule(
            category=cls.CATEGORY,
            title=cls.TITLE,
            start=start,
            end=end_datetime,
            detail=detail,
        )
