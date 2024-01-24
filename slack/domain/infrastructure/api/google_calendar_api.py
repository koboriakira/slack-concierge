from abc import ABCMeta, abstractmethod
from typing import Optional
from datetime import datetime as DatetimeObject
from datetime import date as DateObject
from domain.schedule.schedule import Schedule


class GoogleCalendarApi(metaclass=ABCMeta):
    @abstractmethod
    def get_gas_calendar(self,
                         date: DateObject) -> list[dict]:
        """ カレンダーを取得する """
        pass

    @abstractmethod
    def get_current_schedules(self) -> list[dict]:
        """ 直近のスケジュールを取得する。デフォルトで5分先 """
        pass

    @abstractmethod
    def get_gas_calendar_achievements(self,
                                      date: DateObject) -> list[dict]:
        """ 実績を取得する """
        pass

    @abstractmethod
    def delete_gas_calendar(self,
                            date: DateObject,
                            category: str,
                            title: str) -> dict:
        """ カレンダーを削除する """
        pass

    @abstractmethod
    def post_schedule(self, schedule: Schedule) -> bool:
        """ カレンダーを追加する """
        pass
