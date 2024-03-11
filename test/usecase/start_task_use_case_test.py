from unittest import TestCase
from unittest.mock import Mock

import pytest
from slack.domain.channel import ChannelType
from slack.domain.infrastructure.api.google_calendar_api import GoogleCalendarApi
from slack.domain.task import Task, TaskRepository
from slack.usecase.service.event_bridge_scheduler_service import EventBridgeSchedulerService, PomodoroTimerRequest
from slack.usecase.start_task_use_case import StartTaskError, StartTaskUseCase
from slack_sdk.web import WebClient

DEMO_TS = "1710086804.368969"

class StartTaskUseCaseTest(TestCase):
    def setUp(self) -> None:
        # TaskRepositoryのモックを作成
        task_repository = Mock(spec=TaskRepository)
        google_cal_api = Mock(spec=GoogleCalendarApi)
        client=Mock(spec=WebClient)
        scheduler_service=Mock(spec=EventBridgeSchedulerService)

        self.suite = StartTaskUseCase(
            task_repository=task_repository,
            google_cal_api=google_cal_api,
            client=client,
            scheduler_service=scheduler_service,
        )

        self.suite.client.chat_postMessage.return_value = {"ts": DEMO_TS}
        self.suite.task_repository.save.return_value = Task.test_instance()
        self.suite.task_repository.find_by_id.return_value = Task.test_instance()

        return super().setUp()

    def test_タスクIDおよびタスクタイトルが未指定(self) -> None:
        # Given
        task_id = None
        task_title = None

        # Then
        with pytest.raises(StartTaskError):
            self.suite.execute(task_id, task_title)

    def test_タスクタイトルのみ指定(self) -> None:
        # Given
        task_id = None
        task_title = "テスト"

        # When
        task = self.suite.execute(task_id, task_title)

        # Then
        self.suite.task_repository.save.assert_called_once()
        self.suite.task_repository.find_by_id.assert_not_called()
        self.suite.google_cal_api.post_gas_calendar.assert_called_once()
        self.suite.client.chat_postMessage.assert_called_once()
        self.suite.client.reactions_add.assert_called_once()
        self.suite.scheduler_service.set_pomodoro_timer.assert_called_once_with(
            request=PomodoroTimerRequest(
                page_id=task.task_id,
                channel=ChannelType.DIARY.value,
                thread_ts=DEMO_TS,
            ),
        )


    def test_タスクIDのみ指定(self) -> None:
        # Given
        task_id = "test_id"
        task_title = None

        # When
        task = self.suite.execute(task_id, task_title)

        # Then
        self.suite.task_repository.save.assert_not_called()
        self.suite.task_repository.find_by_id.assert_called_once()
        self.suite.google_cal_api.post_gas_calendar.assert_called_once()
        self.suite.client.chat_postMessage.assert_called_once()
        self.suite.client.reactions_add.assert_called_once()
        self.suite.scheduler_service.set_pomodoro_timer.assert_called_once_with(
            request=PomodoroTimerRequest(
                page_id=task.task_id,
                channel=ChannelType.DIARY.value,
                thread_ts=DEMO_TS,
            ),
        )
