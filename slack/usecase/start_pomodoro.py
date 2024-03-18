# FIXME: start_task_use_caseとstart_pomodoroで同じ処理があるので、うまく切り分けること

from datetime import datetime as DateTime

from slack_sdk.web import WebClient

from domain.event_scheduler.pomodoro_timer_request import PomodoroTimerRequest
from domain.infrastructure.api.google_calendar_api import GoogleCalendarApi
from domain.infrastructure.api.notion_api import NotionApi
from domain.task import TaskRepository
from domain_service.block.block_builder import BlockBuilder
from usecase.service.event_bridge_scheduler_service import EventBridgeSchedulerService
from util.datetime import now

POMODORO_ICON = "tomato"

class StartPomodoro:
    def __init__(
        self,
        notion_api: NotionApi,
        google_api: GoogleCalendarApi,
        client: WebClient,
        task_repository: TaskRepository|None = None,
    ):
        from infrastructure.task.notion_task_repository import NotionTaskRepository
        self.notion_api = notion_api
        self.google_api = google_api
        self.client = client
        self.scheduler_service = EventBridgeSchedulerService()
        self.task_repository = task_repository or NotionTaskRepository()

    def handle(self, request: PomodoroTimerRequest):
        """ポモドーロの開始を通達する"""
        _now = now()
        task = self.task_repository.find_by_id(request.page_id)

        # 開始を連絡
        event_ts = self._chat_start_message(
            task_id=request.page_id,
            channel=request.channel,
            thread_ts=request.thread_ts,
        )

        # ポモドーロカウンターをインクリメント
        # FIXME: task.increment_pomodoro_count()を呼び出したあとに保存すればよい
        self.task_repository.update_pomodoro_count(task)
        task.increment_pomodoro_count()

        # Googleカレンダーにイベントを登録する
        self._record_google_calendar_achivement(task_title=task.title, task_url=task.url)

        # 予約投稿を準備
        request = PomodoroTimerRequest(
            page_id=task.task_id,
            channel=request.channel,
            thread_ts=request.thread_ts,
        )
        self.scheduler_service.set_pomodoro_timer(request=request)

        # ポモドーロ開始を示すリアクションをつける
        self.client.reactions_add(
            channel=request.channel, timestamp=event_ts, name=POMODORO_ICON,
        )


    def _chat_start_message(self, task_id: str, channel: str, thread_ts: str) -> str:
        block_builder = BlockBuilder()
        block_builder = block_builder.add_section(text="開始しました！")
        block_builder = block_builder.add_button_action(
            action_id="complete-task",
            text="終了",
            value=self.task_id,
            style="danger",
        )
        block_builder = block_builder.add_context({"page_id": self.task_id})
        blocks = block_builder.build()
        response = self.client.chat_postMessage(
            text="", blocks=blocks, channel=channel, thread_ts=thread_ts,
        )
        event_ts = response["ts"]
        return event_ts

    def _record_google_calendar_achivement(
        self, page_id: str, start_datetime: DateTime, end_datetime: DateTime,
    ):
        task = self.notion_api.find_task(page_id)
        front_formatter = f"""---
notion_url: {task.url}
---"""
        feeling = task.feeling
        self.google_api.post_gas_calendar(
            start=start_datetime,
            end=end_datetime,
            category="実績",
            title=task.title,
            detail=f"{front_formatter}\n\n{feeling}",
        )


if __name__ == "__main__":
    # python -m usecase.start_pomodoro
    import os

    from infrastructure.api.lambda_google_calendar_api import LambdaGoogleCalendarApi
    from infrastructure.api.lambda_notion_api import LambdaNotionApi

    suite = StartPomodoro(
        notion_api=LambdaNotionApi(),
        google_api=LambdaGoogleCalendarApi(),
        client=WebClient(token=os.environ["SLACK_BOT_TOKEN"]),
    )
    suite.handle(
        notion_page_block_id="73a38586-6754-4636-9a7c-173bcbdc4d1d",
        channel="C01JYJY6Z3V",
        thread_ts="1618125139.000300",
    )
