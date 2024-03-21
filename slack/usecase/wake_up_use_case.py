from domain.schedule.achievement import Achievement
from domain.schedule.achievement_repository import AchievementRepository
from util.datetime import jst_now


class WakeUpUseCase:
    def __init__(self, achievement_repository: AchievementRepository) -> None:
        self._achievement_repository = achievement_repository

    def execute(self) -> list:
        # 「起床」の実績を記録
        wakeup_achivement = Achievement.wakeup(wakeup_at=jst_now())
        self._achievement_repository.save(wakeup_achivement)
