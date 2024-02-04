from datetime import datetime as DateTime
from datetime import timedelta
from slack_sdk.web import WebClient
from domain.infrastructure.api.notion_api import NotionApi
from domain.infrastructure.api.google_calendar_api import GoogleCalendarApi
from domain_service.block.block_builder import BlockBuilder
from util.datetime import now
from usecase.service.event_bridge_scheduler_service import EventBridgeSchedulerService
from domain.event_scheduler.pomodoro_timer_request import PomodoroTimerRequest

class StartPomodoro:
    def __init__(self, notion_api: NotionApi, google_api: GoogleCalendarApi, client: WebClient):
        self.notion_api = notion_api
        self.google_api = google_api
        self.client = client
        self.scheduler_service = EventBridgeSchedulerService()

    def handle(self, request: PomodoroTimerRequest):
        """ ポモドーロの開始を通達する """
        _now = now()

        # 開始を連絡
        event_ts = self._chat_start_message(channel=request.channel, thread_ts=request.thread_ts)

        # ポモドーロカウンターをインクリメント
        self.notion_api.update_pomodoro_count(page_id=request.page_id)

        # Googleカレンダーに実績を記録
        self._record_google_calendar_achivement(
            page_id=request.page_id,
            start_datetime=_now,
            end_datetime=_now + timedelta(minutes=25),
        )

        self.scheduler_service.set_pomodoro_timer(request=request)

        self.client.reactions_add(channel=request.channel, timestamp=event_ts, name="tomato")


    def _chat_start_message(self, channel: str, thread_ts: str) -> str:
        block_builder = BlockBuilder()
        block_builder = block_builder.add_section(
            text=f"開始しました！"
        )
        blocks = block_builder.build()
        response = self.client.chat_postMessage(text="", blocks=blocks, channel=channel, thread_ts=thread_ts)
        event_ts = response["ts"]
        return event_ts

    def _record_google_calendar_achivement(self, page_id: str, start_datetime: DateTime, end_datetime: DateTime):
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
    from infrastructure.api.lambda_notion_api import LambdaNotionApi
    from infrastructure.api.lambda_google_calendar_api import LambdaGoogleCalendarApi
    import os

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
