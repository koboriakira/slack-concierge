from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock

from slack.domain.schedule.achievement_repository import AchievementRepository
from slack.usecase.remind_to_record_achivement_use_case import RemindToRecordAchievementUseCase
from slack_sdk.web import WebClient

DEMO_START_DATETIME = datetime(2024, 3, 16, 11, 0, 0)
DEMO_END_DATETIME = datetime(2024, 3, 16, 13, 0, 0)
DEMO_CHANNEL_ID = "channel_id"
DEMO_THREAD_TS = "thread_ts"

class TestRemindToRecordAchievementUseCase(TestCase):
    def setUp(self) -> None:
        achievement_repository = Mock(spec=AchievementRepository)
        slack_bot_client = Mock(spec=WebClient)

        self.suite = RemindToRecordAchievementUseCase(
            achievement_repository=achievement_repository,
            slack_client=slack_bot_client,
        )

        return super().setUp()

    def test_実績がある場合(self) -> None:
        # Given
        self.suite.achievement_repository.search.return_value = [
            Mock(),
            Mock(),
        ]

        # When
        self.suite.execute(DEMO_START_DATETIME, DEMO_END_DATETIME, DEMO_CHANNEL_ID)

        # Then
        self.suite.slack_client.chat_postMessage.assert_not_called()

    def test_実績がない場合(self) -> None:
        # Given
        self.suite.achievement_repository.search.return_value = []

        # When
        self.suite.execute(DEMO_START_DATETIME, DEMO_END_DATETIME, DEMO_CHANNEL_ID)

        # Then
        self.suite.slack_client.chat_postMessage.assert_called_once()
