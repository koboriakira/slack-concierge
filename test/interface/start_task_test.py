from unittest import TestCase
from unittest.mock import Mock

from slack.interface.start_task import StartTaskInterface


class StartTaskTest(TestCase):
    def setUp(self) -> None:
        start_task_use_case = Mock()
        self.suite = StartTaskInterface(
            start_task_use_case=start_task_use_case,
        )
        return super().setUp()

    def test_新規タスクを作成(self) -> None:
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
        self.suite.start_task_use_case.execute.assert_called_once_with(task_id=None, task_title="test")
