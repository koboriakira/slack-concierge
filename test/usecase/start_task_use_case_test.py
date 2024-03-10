from unittest import TestCase

import pytest
from slack.usecase.start_task_use_case import StartTaskError, StartTaskUseCase


class StartTaskUseCaseTest(TestCase):
    def setUp(self) -> None:
        self.suite = StartTaskUseCase()
        return super().setUp()

    def test_タスクIDおよびタスクタイトルが未指定(self) -> None:
        # Given
        task_id = None
        task_title = None

        # Then
        with pytest.raises(StartTaskError):
            self.suite.execute(task_id, task_title)
