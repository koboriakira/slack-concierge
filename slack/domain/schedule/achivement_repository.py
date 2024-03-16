from abc import ABCMeta, abstractmethod
from datetime import datetime

from domain.schedule.achivement import Achievement


class AchivementRepository(metaclass=ABCMeta):
    @abstractmethod
    def search(self, start: datetime, end: datetime) -> Achievement:
        pass
