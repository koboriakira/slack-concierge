# FIXME: start_task_use_caseとstart_pomodoroで同じ処理があるので、うまく切り分けること

import logging
from datetime import timedelta

from slack_sdk.web import WebClient

from domain.channel import ChannelType
from domain.infrastructure.api.google_calendar_api import GoogleCalendarApi
from domain.task import Task, TaskRepository
from usecase.service.event_bridge_scheduler_service import EventBridgeSchedulerService, PomodoroTimerRequest
from util.datetime import jst_now
from util.environment import Environment


# 独自の例外
class StartTaskError(Exception):
    @staticmethod
    def unspecified() -> "StartTaskError":
        return StartTaskError("タスクIDおよびタスクタイトルが未指定です")


CHANNEL = ChannelType.DIARY if not Environment.is_demo() else ChannelType.TEST
POMODORO_ICON = "tomato"

class StartTaskUseCase:
    def __init__(
            self,
            task_repository: TaskRepository | None = None,
            google_cal_api: GoogleCalendarApi | None = None,
            client: WebClient | None = None,
            scheduler_service: EventBridgeSchedulerService | None = None,
            logger: logging.Logger | None = None) -> None:
        from infrastructure.api.lambda_google_calendar_api import LambdaGoogleCalendarApi
        from infrastructure.task.notion_task_repository import NotionTaskRepository
        self.task_repository = task_repository or NotionTaskRepository()
        self.google_cal_api = google_cal_api or LambdaGoogleCalendarApi()
        self.client = client or WebClient(token=Environment.get_slack_bot_token())
        self.scheduler_service = scheduler_service or EventBridgeSchedulerService(logger=logger)
        self.logger = logger or logging.getLogger(__name__)

    def execute(self, task_id: str | None = None, task_title: str | None = None) -> Task:
        if task_id is None and task_title is None:
            raise StartTaskError.unspecified()
        task = self.load_or_create(task_id=task_id, task_title=task_title)

        # InProgressに更新、ポモドーロカウンターをインクリメント
        task.increment_pomodoro_count()
        task.inprogress()
        self.task_repository.save(task)

        # Googleカレンダーにイベントを登録する
        self._record_google_calendar_achivement(task_title=task.title, task_url=task.url)

        # Slackに投稿
        text, blocks = task.create_slack_message_start_task()
        response = self.client.chat_postMessage(channel=CHANNEL.value, text=text, blocks=blocks)
        event_ts = response["ts"]

        # 予約投稿を準備
        request = PomodoroTimerRequest(
            page_id=task.task_id,
            channel=CHANNEL.value,
            thread_ts=event_ts,
            event_ts=event_ts,
        )
        self.scheduler_service.set_pomodoro_timer(request=request)

        return task

    def load_or_create(self, task_id: str|None = None, task_title: str|None = None) -> Task:
        if task_id is not None:
            return self.task_repository.find_by_id(task_id)

        # いまスタートするので、「今すぐやる」タスクとして作成する
        task = Task(
            title=task_title,
            start_date=jst_now().replace(hour=0, minute=0, second=0, microsecond=0),
            task_kind="今すぐやる",
        )
        return self.task_repository.save(task)

    def _record_google_calendar_achivement(self, task_title: str, task_url: str) -> None:
        start = jst_now()
        end = start + timedelta(minutes=25)
        front_formatter = f"""---
notion_url: {task_url}
---"""
        self.google_cal_api.post_gas_calendar(
            start=start,
            end=end,
            category="実績",
            title=task_title,
            detail=f"{front_formatter}",
        )

if __name__ == "__main__":
    # python -m slack.usecase.start_task_use_case
    suite = StartTaskUseCase()
    print(suite.execute(task_id="5f0093cb611d444d86c513133ab4178a"))
