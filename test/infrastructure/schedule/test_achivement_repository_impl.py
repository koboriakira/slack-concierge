from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock

import pytest
from slack.domain.infrastructure.api.google_calendar_api import GoogleCalendarApi
from slack.infrastructure.api.lambda_google_calendar_api import LambdaGoogleCalendarApi
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

    @pytest.mark.learning()
    def test_正常系(self) -> None:
        # 実行前に.envを読み込むこと
        import logging
        logging.basicConfig(level=logging.DEBUG)
        repository = AchivementRepositoryImpl(google_cal_api=LambdaGoogleCalendarApi())

        repository.search(datetime(2024, 3, 15), datetime(2024, 3, 16))
