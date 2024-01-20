from datetime import datetime as DatetimeObject
from datetime import date as DateObject
from datetime import timedelta
from typing import Optional
import jpholiday



def get_current_day_and_tomorrow(date_str: Optional[str] = None) -> tuple[float, float]:
    """
    指定された日付の0時と翌日の0時のunixtimeを返す。
    指定がない場合は今日の0時と翌日の0時のunixtimeを返す。
    """
    if date_str is None:
        today = DatetimeObject.now()
        return get_current_day_and_tomorrow(date_str=today.strftime("%Y-%m-%d"))

    selected_date = DatetimeObject.strptime(date_str, "%Y-%m-%d")
    unix_today = DatetimeObject(selected_date.year, selected_date.month,
                                selected_date.day).timestamp()
    unix_tomorrow = unix_today + 86400
    return unix_today, unix_tomorrow


def is_holiday(date: DateObject) -> bool:
    """
    指定された日付が休日かどうかを判定する。
    """
    if date.weekday() >= 5:
        return True
    return jpholiday.is_holiday(date)


def is_first_or_third_week_thursday(date: DateObject) -> bool:
    # dateが第1週もしくは第3週の木曜日であるかどうかを判定する
    first_day = date.replace(day=1)
    days = (3-first_day.weekday()) % 7
    first_thursday = (
        first_day + timedelta(days))
    first_week_thursday = first_thursday
    third_week_thursday = first_thursday + timedelta(days=14)
    return date == first_week_thursday or date == third_week_thursday
