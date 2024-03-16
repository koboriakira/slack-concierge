from abc import ABCMeta, abstractmethod
from datetime import date as DateObject
from datetime import datetime as DatetimeObject

from domain.schedule.schedule import Schedule


class GoogleCalendarApi(metaclass=ABCMeta):
    @abstractmethod
    def get_gas_calendar(self,
                         date: DateObject) -> list[dict]:
        """ カレンダーを取得する """

    @abstractmethod
    def get_current_schedules(self) -> list[dict]:
        """ 直近のスケジュールを取得する。デフォルトで5分先 """

    @abstractmethod
    def get_gas_calendar_achievements(self,
                                      date: DateObject) -> list[dict]:
        """ 実績を取得する """

    @abstractmethod
    def delete_gas_calendar(self,
                            date: DateObject,
                            category: str,
                            title: str) -> dict:
        """ カレンダーを削除する """

    @abstractmethod
    def post_schedule(self, schedule: Schedule) -> bool:
        """ カレンダーを追加する """

    @abstractmethod
    def post_gas_calendar(self,
                          start: DatetimeObject,
                          end: DatetimeObject,
                          category: str,
                          title: str,
                          detail: str | None = None) -> bool:
        """ カレンダーを追加する """

    @abstractmethod
    def get(self, path: str, params: dict) -> list[dict]:
        pass
