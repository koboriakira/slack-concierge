import logging
from unittest import TestCase
from unittest.mock import Mock

from slack.domain.channel.channel_type import ChannelType
from slack.domain.task.task import Task
from slack.interface.start_task import StartTaskInterface
from slack.usecase.service.event_bridge_scheduler_service import EventBridgeSchedulerService, PomodoroTimerRequest
from slack.usecase.start_task_use_case import StartTaskUseCase
from slack_sdk import WebClient


class StartTaskTest(TestCase):
    def setUp(self) -> None:
        logger = Mock(spec=logging.Logger)
        client = Mock(spec=WebClient)
        start_task_use_case = Mock(spec=StartTaskUseCase)
        scheduler_service = Mock(spec=EventBridgeSchedulerService)
        self.suite = StartTaskInterface(
            client=client,
            channel=ChannelType.TEST,
            start_task_use_case=start_task_use_case,
            scheduler_service=scheduler_service,
            logger=logger)
        return super().setUp()

    def test_新規タスクを作成(self) -> None:
        # Mock
        demo_ts = "1710086804.368969"
        self.suite.client.chat_postMessage.return_value = {"ts": demo_ts}
        demo_task = Task.test_instance()
        self.suite.start_task_use_case.execute.return_value = demo_task

        # Given
        view = {
          "state": {
            "values": {
                "QSU6q": {
                    "new-task": {
                        "type": "plain_text_input",
                        "value": "test",
                    },
                },
            },
        }}

        # When
        self.suite.start_task(view=view)

        # Then
        self.suite.client.chat_postMessage.assert_called_once()
        self.suite.client.reactions_add.assert_called_once()
        self.suite.scheduler_service.set_pomodoro_timer.assert_called_once_with(
            request=PomodoroTimerRequest(
                page_id=demo_task.task_id,
                channel=ChannelType.TEST.value,
                thread_ts=demo_ts,
            ),
        )
