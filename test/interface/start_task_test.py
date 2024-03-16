from unittest import TestCase
from unittest.mock import Mock

from slack.interface.start_task import StartTaskInterface, StartTaskModalInterface
from slack.usecase.fetch_current_tasks_use_case import FetchCurrentTasksUseCase
from slack.usecase.start_task_use_case import StartTaskUseCase


class StartTaskTest(TestCase):
    def setUp(self) -> None:
        start_task_use_case=Mock(spec=StartTaskUseCase)
        self.start_task_interface = StartTaskInterface(
            start_task_use_case=start_task_use_case,
        )

        fetch_current_tasks_use_case=Mock(spec=FetchCurrentTasksUseCase)
        fetch_current_tasks_use_case.execute.return_value = []
        self.start_task_modal_interface = StartTaskModalInterface(
            fetch_current_tasks_use_case=fetch_current_tasks_use_case,
            client=Mock(),
        )
        return super().setUp()

    def test_モーダルを開く(self) -> None:
        # Given
        trigger_id = "trigger_id"

        # When
        self.start_task_modal_interface.execute(trigger_id=trigger_id)

        # Then
        self.start_task_modal_interface.fetch_current_tasks_use_case.execute.assert_called_once()

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
        self.start_task_interface.start_task(view=view)

        # Then
        self.start_task_interface.start_task_use_case.execute.assert_called_once_with(task_id=None, task_title="test")
