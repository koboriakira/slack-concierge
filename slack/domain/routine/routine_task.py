from enum import Enum
from datetime import datetime as Datetime
from datetime import timedelta
from util.datetime import now as datetime_now

def burnable_garbate_date() -> Datetime:
    now = datetime_now()
    match now.weekday():
        case 0:
            return now + timedelta(days=1)
        case 1:
            return now + timedelta(days=3)
        case 2:
            return now + timedelta(days=2)
        case 3:
            return now + timedelta(days=1)
        case 4:
            return now + timedelta(days=4)
        case 5:
            return now + timedelta(days=3)
        case 6:
            return now + timedelta(days=2)




class RoutineTask(Enum):
    """ ルーティンタスク """
    # {"家事": "housework"},
    # {"料理": "cooking"},
    # {"買い物": "shopping"},
    # {"朝食": "breakfast"},
    # {"昼食": "lunch"},
    # {"夕食": "dinner"},
    # {"入浴": "bath"},
    # {"睡眠": "sleep"},
    # {"週次レビュー": "weekly-review"},
    # {"月次レビュー": "monthly-review"},
    # {"その他": "other"},
    MORNING_HOUSEWORK = "朝の家事"
    AFTERNOON_HOUSEWORK = "昼の家事"
    CLEANING_BATHROOM = "風呂掃除"
    DAILY_REVIEW = "日次レビュー"
    WEEKLY_REVIEW = "週次レビュー"
    CLEANING_TOILET = "トイレ掃除"
    BURNABLE_GARBAGE = "可燃ごみ"
    # UNBURNABLE_GARBAGE = "不燃ごみ"
    RECYCLABLE_GARBAGE = "資源ごみ"


    @property
    def datetime_creates_next_task(self) -> Datetime:
        """ 次回のタスクの実行日時。00:00は日付のみの指定とする """
        now = datetime_now()
        match self:
            case RoutineTask.CLEANING_BATHROOM:
                # 翌週
                target_datetime = now + timedelta(days=7)
                return target_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            case RoutineTask.MORNING_HOUSEWORK:
                # 翌日9:30
                target_datetime = now + timedelta(days=1)
                return target_datetime.replace(hour=9, minute=30, second=0, microsecond=0)
            case RoutineTask.AFTERNOON_HOUSEWORK:
                # 翌日12:00
                target_datetime = now + timedelta(days=1)
                return target_datetime.replace(hour=12, minute=0, second=0, microsecond=0)
            case RoutineTask.DAILY_REVIEW:
                # 翌日22:00
                target_datetime = now + timedelta(days=1)
                return target_datetime.replace(hour=22, minute=0, second=0, microsecond=0)
            case RoutineTask.WEEKLY_REVIEW:
                # 翌週土曜日
                target_datetime = now + timedelta(days=(5 - now.weekday() + 7) % 7)
                return target_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            case RoutineTask.CLEANING_TOILET:
                # 2日後
                target_datetime = now + timedelta(days=2)
                return target_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            case RoutineTask.BURNABLE_GARBAGE:
                # 今日が金、土、日、月の場合は火曜日、火、水、木の場合は金曜日
                target_datetime = burnable_garbate_date()
                return target_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            case RoutineTask.RECYCLABLE_GARBAGE:
                # 次の水曜日
                target_datetime = now + timedelta(days=(2 - now.weekday() + 7) % 7)
                return target_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
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


if __name__ == "__main__":
    # python -m domain.routine.routine_task
    now = datetime_now()
    print(now.date().weekday())
