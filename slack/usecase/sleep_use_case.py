from logging import Logger

from domain.schedule.achievement import Achievement
from domain.schedule.achievement_repository import AchievementRepository
from util.datetime import jst_now


class SleepUseCase:
    def __init__(self, achievement_repository: AchievementRepository, logger: Logger) -> None:
        self._achievement_repository = achievement_repository
        self._logger = logger

    def execute(self) -> list:
        # 「起床」の実績を記録
        self._logger.info("就寝実績を記録します")
        wakeup_achivement = Achievement.sleep(sleep_at=jst_now())
        self._achievement_repository.save(wakeup_achivement)
