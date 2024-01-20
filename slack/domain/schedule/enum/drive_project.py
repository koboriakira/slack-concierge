from domain.schedule.schedule import Schedule, Detail, SubTask
from datetime import timedelta
from datetime import datetime as DatetimeObject


class DriveProject:
    CATEGORY = "プライベート"
    MARGIN = 60

    @classmethod
    def create(cls, start: DatetimeObject, title: str, notion_url: str, tasks: list[dict]) -> Schedule:
        sub_tasks = _calculate_sub_tasks(tasks)
        detail = Detail(
            memo=[notion_url],
            sub_tasks=sub_tasks
        )
        return Schedule(
            category=cls.CATEGORY,
            title=title,
            start=start,
            end=start + timedelta(minutes=cls.MARGIN),
            detail=detail,
        )

def _calculate_sub_tasks(tasks: list[dict]) -> list[SubTask]:
    """ サブタスクの時間を計算する """
    DEFAULT_MINUTES = 15

    if len(tasks) == 0:
        return []
    sum_minutes = 0
    sub_tasks:list[SubTask] = []
    _tasks = tasks
    while True and len(_tasks) > 0:
        task = _tasks.pop()
        minutes = task["minutes"] if "minutes" in task else DEFAULT_MINUTES
        sum_minutes += minutes
        if sum_minutes < 60:
            sub_task = SubTask(name=f"{task['title']} ({minutes})")
            sub_tasks.append(sub_task)
        else:
            # 残りのタスクがあればメモにまとめる
            sub_task = SubTask(name=f"{task['title']} ({minutes})",
                               memo=[f"他{len(_tasks)}件"])
            sub_tasks.append(sub_task)
            break
    return sub_tasks
