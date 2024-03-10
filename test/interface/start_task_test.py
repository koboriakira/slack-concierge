from unittest import TestCase
from unittest.mock import Mock

from slack.interface.start_task import start_task_refactored


class StartTaskTest(TestCase):
    def test_start_task_refactored(self) -> None:
        # Given
        logger = Mock()
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
        client = Mock()
        client.chat_postMessage.return_value = {"ts": "1710086804.368969"}

        # When
        start_task_refactored(logger=logger, view=view, client=client)

        # Then
        client.chat_postMessage.assert_called_once()
        client.reactions_add.assert_called_once()
        client.views_open.assert_not_called()
