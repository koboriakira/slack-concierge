from logging import Logger

from domain.schedule.achievement import Achievement
from domain.schedule.achievement_repository import AchievementRepository
from util.datetime import jst_now


class ComeHomeUseCase:
    def __init__(self, achievement_repository: AchievementRepository, logger: Logger) -> None:
        self._achievement_repository = achievement_repository
        self._logger = logger

    def execute(self) -> list:
        self._logger.info("外出実績を記録します")
        go_out_achivement = Achievement.come_home(come_home_at=jst_now())
        self._achievement_repository.save(go_out_achivement)
