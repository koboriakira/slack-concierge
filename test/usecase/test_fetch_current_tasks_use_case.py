from datetime import timedelta
from unittest import TestCase
from unittest.mock import Mock

from slack.domain.task import TaskRepository
from slack.infrastructure.repository.current_tasks_s3_repository import CurrentTasksS3Repository
from slack.usecase.fetch_current_tasks_use_case import FetchCurrentTasksUseCase
from slack.util.datetime import jst_now

DEMO_TS = "1710086804.368969"

class TestFetchCurrentTasksUseCase(TestCase):
    def setUp(self) -> None:
        # TaskRepositoryのモックを作成
        task_repository = Mock(spec=TaskRepository)
        current_tasks_s3_repository = Mock(spec=CurrentTasksS3Repository)
        self.suite = FetchCurrentTasksUseCase(
            task_repository=task_repository,
            current_tasks_s3_repository=current_tasks_s3_repository,
        )
        return super().setUp()

    def test_キャッシュが見つからない場合(self) -> None:
        # Given
        self.suite.current_tasks_s3_repository.load.return_value = None
        self.suite.task_repository.fetch_current_tasks.return_value = []

        # When
        _ = self.suite.execute()

        # Then
        self.suite.task_repository.fetch_current_tasks.assert_called_once()
        self.suite.current_tasks_s3_repository.save.assert_called_once()


    def test_キャッシュが見つかった場合(self) -> None:
        # Given
        expires_at = jst_now() + timedelta(minutes=5)
        current_tasks_cache = {
            "task_options": [],
            "expires_at": expires_at.isoformat(),
        }
        # Given
        self.suite.current_tasks_s3_repository.load.return_value = current_tasks_cache

        # When
        _ = self.suite.execute()

        # Then
        self.suite.task_repository.fetch_current_tasks.assert_not_called()
        self.suite.current_tasks_s3_repository.save.assert_not_called()
