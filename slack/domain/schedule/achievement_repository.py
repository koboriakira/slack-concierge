from abc import ABCMeta, abstractmethod
from datetime import datetime

from domain.schedule.achievement import Achievement


class AchievementRepository(metaclass=ABCMeta):
    @abstractmethod
    def search(self, start: datetime, end: datetime) -> Achievement:
        pass
