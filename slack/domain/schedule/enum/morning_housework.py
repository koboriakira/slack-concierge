from domain.schedule.schedule import Schedule, SubTask, Detail
from datetime import timedelta
from datetime import datetime as DatetimeObject
from typing import Optional


class MorningHousework:
    CATEGORY = "朝の予定"
    TITLE = "朝の家事"
    MARGIN = 30

    @classmethod
    def create(cls, start: DatetimeObject) -> Schedule:
        sub_tasks = []
        sub_tasks.append(SubTask(name="洗濯"))
        sub_tasks.append(SubTask(name="コーヒーを淹れる"))
        sub_tasks.append(SubTask(name="居間の片付け"))
        sub_tasks.append(SubTask(name="食器を洗う"))
        sub_tasks.append(SubTask(name="トイレ掃除"))
        sub_tasks.append(SubTask(name="ロボット掃除機の掃除"))
        sub_tasks.append(SubTask(name="洗顔、ひげそり"))
        sub_tasks.append(SubTask(name="乾燥機に入れる"))
        detail = Detail(sub_tasks=sub_tasks)
        end_datetime = start + timedelta(minutes=cls.MARGIN)
        return Schedule(
            category=cls.CATEGORY,
            title=cls.TITLE,
            start=start,
            end=end_datetime,
            detail=detail,
        )
