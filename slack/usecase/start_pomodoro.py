from datetime import datetime as DateTime
from datetime import timedelta
from slack_sdk.web import WebClient
from domain.infrastructure.api.notion_api import NotionApi
from domain.infrastructure.api.google_calendar_api import GoogleCalendarApi
from domain_service.block.block_builder import BlockBuilder
from util.datetime import now


class StartPomodoro:
    def __init__(self, notion_api: NotionApi, google_api: GoogleCalendarApi, client: WebClient):
        self.notion_api = notion_api
        self.google_api = google_api
        self.client = client

    def handle(self, notion_page_block_id: str, channel: str, thread_ts: str):
        """ ポモドーロの開始を通達する """
        _now = now()

        # 開始を連絡
        self._chat_start_message(channel=channel, thread_ts=thread_ts)

        # ポモドーロカウンターをインクリメント
        self.notion_api.update_pomodoro_count(page_id=notion_page_block_id)

        # Googleカレンダーに実績を記録
        self._record_google_calendar_achivement(
            page_id=notion_page_block_id,
            start_datetime=_now,
            end_datetime=_now + timedelta(minutes=25),
        )

        # TODO: 25分後に終了を通知したい。EventBridgeなどを使う必要がありそうで時間がかかるので、
        # とりあえず開始直後に通知するようにしておいて、机上のタイマーで測っておく
        # そのため以下はEventBridge実装後に移行する
        block_builder = BlockBuilder()
        block_builder = block_builder.add_section(
            text=f"25分が経過しました！\n「気持ち」を記録して休憩してください"
        )
        block_builder = block_builder.add_button_action(
            action_id="start-pomodoro",
            text="再開",
            value=notion_page_block_id,
            style="primary",
        )
        block_builder = block_builder.add_button_action(
            action_id="complete-task",
            text="終了",
            value=notion_page_block_id,
            style="danger",
        )
        block_builder = block_builder.add_context({
            "channel_id": channel,
            "thread_ts": thread_ts,
            })
        blocks = block_builder.build()
        self.client.chat_postMessage(text="", blocks=blocks, channel=channel, thread_ts=thread_ts)


        # TODO: record-feelingは削除する
        # block_builder = BlockBuilder()
        # block_builder = block_builder.add_section(
        #     text=f"25分が経過しました！\n「気持ち」を記録して休憩してください"
        # )
        # block_builder = block_builder.add_button_action(
        #     action_id="record-feeling",
        #     text="気持ちを記録",
        #     value=notion_page_block_id,
        #     style="primary",
        # )
        # blocks = block_builder.build()
        # self.client.chat_postMessage(text="", blocks=blocks, channel=channel, thread_ts=thread_ts)

    def _chat_start_message(self, channel: str, thread_ts: str):
        block_builder = BlockBuilder()
        block_builder = block_builder.add_section(
            text=f"開始しました！"
        )
        blocks = block_builder.build()
        self.client.chat_postMessage(text="", blocks=blocks, channel=channel, thread_ts=thread_ts)

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
