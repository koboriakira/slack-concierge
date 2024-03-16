from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock

from slack.domain.infrastructure.api.google_calendar_api import GoogleCalendarApi
from slack.infrastructure.schedule.achivement_repository_impl import AchivementRepositoryImpl

DEMO_START_DATETIME = datetime(2024, 3, 16, 11, 0, 0)
DEMO_END_DATETIME = datetime(2024, 3, 16, 13, 0, 0)
DEMO_CHANNEL_ID = "channel_id"
DEMO_THREAD_TS = "thread_ts"

class TestAchivementRepositoryImpl(TestCase):
    def setUp(self) -> None:
        # TaskRepositoryのモックを作成
        goocle_cal_api = Mock(spec=GoogleCalendarApi)
        self.suite = AchivementRepositoryImpl(google_cal_api=goocle_cal_api)
        return super().setUp()
