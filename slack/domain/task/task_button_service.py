from slack_sdk.web import WebClient

from domain.channel.thread import Thread
from domain.task.task import Task
from domain_service.block.block_builder import BlockBuilder


class TaskButtonSerivce:
    def __init__(
            self,
            slack_client: WebClient) -> None:
        self.slack_client = slack_client

    def execute(
            self,
            task: Task,
            slack_thread: Thread|None = None,
            block_builder: BlockBuilder|None = None,
            is_enabled_complete_button: bool|None = None) -> None:
        slack_thread = slack_thread or Thread.empty()
        block_builder = block_builder or BlockBuilder()

        # Slackの内容を作成
        block_builder = block_builder.add_section(text=task.title_with_link())
        block_builder = block_builder.add_button_action(
            action_id="start-pomodoro",
            text="開始", # TODO: pomodoro_countが0のときは「開始」、それ以外は「再開」
            value=task.task_id,
            style="primary",
        )
        if is_enabled_complete_button:
            block_builder = block_builder.add_button_action(
                action_id="complete-task",
                text="終了",
                value=task.task_id,
                style="danger",
            )
        blocks = block_builder.build()

        # Slackに送信
        self.slack_client.chat_postMessage(
            text="",
            blocks=blocks,
            channel=slack_thread.channel_id,
            thread_ts=slack_thread.thread_ts)
