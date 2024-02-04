from enum import Enum
from datetime import datetime as Datetime
from datetime import timedelta
from util.datetime import now as datetime_now


class RoutineTask(Enum):
    """ ルーティンタスク """
    CLEANING_BATHROOM = "風呂掃除"
    LAUNDRY = "洗濯"
    DAILY_REVIEW = "日次レビュー"
    CLEANING_TOILET = "トイレ掃除"
    # {"家事": "housework"},
    # {"料理": "cooking"},
    # {"買い物": "shopping"},
    # {"朝食": "breakfast"},
    # {"昼食": "lunch"},
    # {"夕食": "dinner"},
    # {"入浴": "bath"},
    # {"睡眠": "sleep"},
    # {"日次レビュー": "daily-review"},
    # {"週次レビュー": "weekly-review"},
    # {"月次レビュー": "monthly-review"},
    # {"その他": "other"},

    @property
    def datetime_creates_next_task(self) -> Datetime:
        """ 次回のタスクの実行日時。00:00は日付のみの指定とする """
        now = datetime_now()
        match self:
            case RoutineTask.CLEANING_BATHROOM:
                target_datetime = now + timedelta(days=7)
                return target_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            case RoutineTask.LAUNDRY:
                target_datetime = now + timedelta(days=1)
                return target_datetime.replace(hour=9, minute=30, second=0, microsecond=0)
            case RoutineTask.DAILY_REVIEW:
                target_datetime = now + timedelta(days=1)
                return target_datetime.replace(hour=22, minute=0, second=0, microsecond=0)
            case _:
                raise NotImplementedError(f"未実装のルーティンタスクです: {self.value}")

    @staticmethod
    def all_options() -> list[dict]:
        return [{
            "text": task.value,
            "value": task.name
        } for task in RoutineTask]

    @staticmethod
    def from_name(name: str) -> 'RoutineTask':
        return RoutineTask(name.replace("【ルーティン】", ""))
