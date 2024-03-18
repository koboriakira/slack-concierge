from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock

from slack.domain.channel.thread import Thread
from slack.domain.schedule.achievement_repository import AchievementRepository
from slack.domain.task.task import Task
from slack.domain.task.task_button_service import TaskButtonSerivce
from slack.domain.task.task_repository import TaskRepository
from slack.usecase.service.event_bridge_scheduler_service import EventBridgeSchedulerService
from slack.usecase.start_pomodoro import StartPomodoro

DEMO_START_DATETIME = datetime(2024, 3, 16, 11, 0, 0)
DEMO_END_DATETIME = datetime(2024, 3, 16, 13, 0, 0)

class TestStartPomodoro(TestCase):
    def setUp(self) -> None:
        task_button_service = Mock(spec=TaskButtonSerivce)
        achievement_repository = Mock(spec=AchievementRepository)
        task_repository = Mock(spec=TaskRepository)
        scheduler_service = Mock(spec=EventBridgeSchedulerService)

        self.suite = StartPomodoro(
            task_button_service=task_button_service,
            achievement_repository=achievement_repository,
            task_repository=task_repository,
            scheduler_service=scheduler_service,
        )

        return super().setUp()

    def test(self):
        # Given
        demo_task = Task.from_title("test")
        demo_start = datetime(2024, 3, 16, 11, 0, 0)
        demo_thread = Thread.create(channel_id="test", thread_ts="test")
        self.suite.task_repository.find_by_id.return_value = demo_task
        self.suite.task_button_service.print_task.return_value = demo_thread

        # When
        self.suite.handle(task_page_id="test", start=demo_start)

        # Then
        self.suite.task_repository.update_pomodoro_count.assert_called_once_with(task=demo_task)
        self.suite.achievement_repository.save.assert_called()
        self.suite.task_button_service.start_pomodoro.assert_called_once_with(
            task=demo_task,
            slack_thread=demo_thread,
        )

        self.suite.scheduler_service.set_pomodoro_timer.assert_called_once()
