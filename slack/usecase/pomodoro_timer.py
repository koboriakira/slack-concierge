
from slack_sdk.web import WebClient

from domain.channel.thread import Thread
from domain.event_scheduler.pomodoro_timer_request import PomodoroTimerRequest
from domain.task.task_button_service import TaskButtonSerivce
from domain.task.task_repository import TaskRepository


class PomodoroTimer:
    def __init__(self, task_button_service: TaskButtonSerivce, task_repository: TaskRepository):
        self.task_button_service = task_button_service
        self.task_repository = task_repository

    def handle(self, request: PomodoroTimerRequest):
        """ ポモドーロの終了を通達する """
        task = self.task_repository.find_by_id(request.page_id)
        if task.is_completed():
            return
        slack_thread = Thread(channel=request.channel, thread_ts=request.thread_ts)
        self.task_button_service.pomodoro_timer(task=task, slack_thread=slack_thread)

    def _is_completed(self, task_id: str):
        """ タスクがすでに完了しているかどうか """
        task = self.notion_api.find_task(task_id)
        return task.is_completed()

if __name__ == "__main__":
    # python -m usecase.pomodoro_timer
    import os

    suite = PomodoroTimer(
        client=WebClient(token=os.environ["SLACK_BOT_TOKEN"]),
    )
    suite.handle(
        notion_page_block_id="62273ee7-be18-4b75-9b52-ca118214c8b5",
        channel="C05F6AASERZ",
        thread_ts="1706668465.883669")
