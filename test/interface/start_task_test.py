import logging
from unittest import TestCase
from unittest.mock import Mock

from slack.interface.start_task import StartTaskInterface
from slack.usecase.service.event_bridge_scheduler_service import EventBridgeSchedulerService
from slack_sdk import WebClient


class StartTaskTest(TestCase):
    def setUp(self) -> None:
        logger = Mock(spec=logging.Logger)
        client = Mock(spec=WebClient)
        scheduler_service = Mock(spec=EventBridgeSchedulerService)
        self.suite = StartTaskInterface(client=client, scheduler_service=scheduler_service, logger=logger)
        return super().setUp()

    def test_start_task_refactored(self) -> None:
        # Given
        view = {
          "state": {
            "values": {
                "iQpPN": {
                    "task": {
                        "type": "static_select",
                        "selected_option": None,
                    },
                },
                "QSU6q": {
                    "new-task": {
                        "type": "plain_text_input",
                        "value": "てすと！",
                    },
                },
                "3V2DC": {
                    "routine-task": {
                        "type": "static_select",
                        "selected_option": None,
                    },
                },
            },
        }}
        self.suite.client.chat_postMessage.return_value = {"ts": "1710086804.368969"}

        # When
        self.suite.start_task(view=view)

        # Then
        self.suite.client.chat_postMessage.assert_called_once()
        self.suite.client.reactions_add.assert_called_once()
        self.suite.client.views_open.assert_not_called()
