from domain.schedule.schedule import Schedule, SubTask, Detail
from datetime import timedelta
from datetime import datetime as DatetimeObject
from datetime import date as DateObject
from typing import Optional
from util.datetime import is_first_or_third_week_thursday


class Resttime:
    CATEGORY = "休息"
    TITLE = "休息"
    MARGIN = 60

    @classmethod
    def create(cls, start: DatetimeObject) -> Schedule:
        sub_tasks = []

        if (garbase_task := cls.__garbage_task(start.date())) is not None:
            sub_tasks.append(SubTask(name=garbase_task))

        sub_tasks.append(SubTask(name="ブログ書く"))
        sub_tasks.append(SubTask(name="明日の予定を作成する"))
        sub_tasks.append(SubTask(name="ストレッチ"))
        detail = Detail(sub_tasks=sub_tasks)
        end_datetime = start + timedelta(minutes=cls.MARGIN)
        return Schedule(
            category=cls.CATEGORY,
            title=cls.TITLE,
            start=start,
            end=end_datetime,
            detail=detail,
        )

    @classmethod
    def __garbage_task(cls, date: DateObject) -> Optional[str]:
        if date.weekday in [1, 4]:
            # 火曜、金曜
            return "燃えるゴミを出す"
        if date.weekday == 2:
            # 水曜
            return "資源ゴミを出す"
        if is_first_or_third_week_thursday(date):
            # 第1、3週の木曜日
            return "燃えないゴミを出す"
        return None
