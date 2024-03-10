

from datetime import datetime as DatetimeObject

from slack_sdk.web import WebClient

from domain.infrastructure.api.google_calendar_api import GoogleCalendarApi
from domain.infrastructure.api.notion_api import NotionApi
from domain.task import Task
from usecase.service.event_bridge_scheduler_service import EventBridgeSchedulerService


class TaskPomodoroCounter:
    def __init__(
        self,
        notion_api: NotionApi,
        google_api: GoogleCalendarApi,
        client: WebClient,
    ) -> None:
        self.notion_api = notion_api
        self.google_api = google_api
        self.client = client
        self.scheduler_service = EventBridgeSchedulerService()

    def countup(self, task: Task) -> None:
        """指定されたタスクのポモドーロを開始する"""
        _now = self._now()

        # ポモドーロカウンターをインクリメント
        task = task.increment_pomodoro_count()

        # Googleカレンダーに実績を記録
        self._record_google_calendar_achivement(
            task=task,
            start_datetime=_now,
            end_datetime=_now + self._timedelta(minutes=25),
        )

        self.scheduler_service.set_pomodoro_timer(request=request)

        self.client.reactions_add(
            channel=request["channel"], timestamp=event_ts, name="tomato",
        )

    def _record_google_calendar_achivement(
        self, task: Task, start_datetime: DatetimeObject, end_datetime: DatetimeObject,
    ) -> None:
        front_formatter = f"""---
notion_url: {task.url}
---"""
        self.google_api.post_gas_calendar(
            start=start_datetime,
            end=end_datetime,
            category="実績",
            title=task.title,
            detail=f"{front_formatter}",
        )
