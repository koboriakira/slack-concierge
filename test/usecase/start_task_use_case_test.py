from unittest import TestCase
from unittest.mock import Mock

import pytest
from slack.domain.infrastructure.api.google_calendar_api import GoogleCalendarApi
from slack.domain.task import Task, TaskRepository
from slack.usecase.start_task_use_case import StartTaskError, StartTaskUseCase


class StartTaskUseCaseTest(TestCase):
    def setUp(self) -> None:
        # TaskRepositoryのモックを作成
        task_repository = Mock(spec=TaskRepository)
        google_cal_api = Mock(spec=GoogleCalendarApi)

        self.suite = StartTaskUseCase(task_repository=task_repository, google_cal_api=google_cal_api)
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

        # task_repository.saveが呼ばれたことを確認
        self.suite.task_repository.save.assert_called_once()
        # task_repository.find_by_idが呼ばれていないことを確認
        self.suite.task_repository.find_by_id.assert_not_called()
        # GoogleCalendarApi.post_gas_calendarが呼ばれたことを確認
        self.suite.google_cal_api.post_gas_calendar.assert_called_once()


    def test_タスクIDのみ指定(self) -> None:
        # Given
        task_id = "test_id"
        task_title = None

        # モックの挙動を設定
        self.suite.task_repository.find_by_id.return_value = Mock(spec=Task)

        # When
        task = self.suite.execute(task_id, task_title)

        # Then
        # task_repository.saveが呼ばれていないことを確認
        self.suite.task_repository.save.assert_not_called()
        # task_repository.find_by_idが呼ばれたことを確認
        self.suite.task_repository.find_by_id.assert_called_once()
        # GoogleCalendarApi.post_gas_calendarが呼ばれたことを確認
        self.suite.google_cal_api.post_gas_calendar.assert_called_once()
