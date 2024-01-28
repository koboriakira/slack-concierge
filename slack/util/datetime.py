from datetime import datetime as DatetimeObject
from datetime import date as DateObject
from datetime import timedelta
from datetime import timezone
from typing import Optional
import jpholiday

JST = timezone(timedelta(hours=+9), "JST")


def now(enable_jst: bool = True) -> DatetimeObject:
    """
    タイムゾーンを指定して現在時刻を取得する。
    意図的にUTC+00:00を指定する場合はenable_jst=Falseとする。
    """
    return DatetimeObject.now(JST if enable_jst else timezone.utc)
def fromtimestamp(timestamp:float, enable_jst: bool = True) -> DatetimeObject:
    """
    タイムゾーンを指定して現在時刻を取得する。
    意図的にUTC+00:00を指定する場合はenable_jst=Falseとする。
    """
    return DatetimeObject.fromtimestamp(timestamp, JST if enable_jst else timezone.utc)


def get_current_day_and_tomorrow(date_str: Optional[str] = None) -> tuple[float, float]:
    """
    指定された日付の0時と翌日の0時のunixtimeを返す。
    指定がない場合は今日の0時と翌日の0時のunixtimeを返す。
    """
    if date_str is None:
        today = now()
        return get_current_day_and_tomorrow(date_str=today.strftime("%Y-%m-%d"))

    selected_date = DatetimeObject.strptime(date_str, "%Y-%m-%d")
    unix_today = DatetimeObject(year=selected_date.year,
                                month=selected_date.month,
                                day=selected_date.day,
                                tzinfo=JST).timestamp()
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
