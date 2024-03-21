from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock

from slack.infrastructure.schedule.achievement_repository_impl import AchievementRepositoryImpl
from slack.usecase.wake_up_use_case import WakeUpUseCase

DEMO_START_DATETIME = datetime(2024, 3, 16, 11, 0, 0)
DEMO_END_DATETIME = datetime(2024, 3, 16, 13, 0, 0)

class TestWakeUpUseCase(TestCase):
    def setUp(self) -> None:
        achievement_repository = Mock(spec=AchievementRepositoryImpl)
        self.suite = WakeUpUseCase(
            achievement_repository=achievement_repository,
        )
        return super().setUp()

    def test(self):
        # When
        self.suite.execute()

        # Then
        self.suite._achievement_repository.save.assert_called()
