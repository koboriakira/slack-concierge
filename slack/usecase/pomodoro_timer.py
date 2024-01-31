from slack_sdk.web import WebClient
from domain_service.block.block_builder import BlockBuilder
from domain.user import UserKind


class PomodoroTimer:
    def __init__(self, client: WebClient):
        self.client = client

    def handle(self, notion_page_block_id: str, channel: str, thread_ts: str):
        """ ポモドーロの終了を通達する """
        user_mention = UserKind.KOBORI_AKIRA.mention()

        block_builder = BlockBuilder()
        block_builder = block_builder.add_section(
            text=f"{user_mention}\n25分が経過しました！\n進捗や気持ちをメモして休憩してください。"
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
