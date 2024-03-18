

from domain.channel.thread import Thread
from domain.task.task_button_service import TaskButtonSerivce
from domain.task.task_repository import TaskRepository


class PomodoroTimer:
    def __init__(self, task_button_service: TaskButtonSerivce, task_repository: TaskRepository) -> None:
        self.task_button_service = task_button_service
        self.task_repository = task_repository

    def handle(self, task_page_id: str, slack_thread: Thread) -> None:
        """ ポモドーロの終了を通達する """
        task = self.task_repository.find_by_id(task_page_id)
        if task.is_completed():
            return
        self.task_button_service.pomodoro_timer(task=task, slack_thread=slack_thread)
