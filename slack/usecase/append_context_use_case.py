import os

from slack_sdk.web import WebClient

from domain.user.user_kind import UserKind
from domain_service.block.block_builder import BlockBuilder


class AppendContextUseCase:
    def __init__(
            self,
            slack_bot_client: WebClient|None = None,
            slack_user_client: WebClient|None = None) -> None:
        self.slack_bot_client = slack_bot_client or WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        self.slack_user_client = slack_user_client or WebClient(token=os.environ["SLACK_USER_TOKEN"])


    def execute(self, channel: str, event_ts: str, data: dict) -> None:
        messages = self.slack_bot_client.conversations_history(channel=channel)["messages"]
        message = next((message for message in messages if message["ts"] == event_ts), None)
        if message is None:
            error_message = f"Message not found. channel: {channel}, event_ts: {event_ts}"
            raise ValueError(error_message)

        text = message.get("text", "")
        blocks = message.get("blocks", [])
        block_builder = BlockBuilder(blocks)
        block_builder = block_builder.append_context(data)
        blocks = block_builder.build()

        slack_web_client = self._get_web_client(message["user"])
        slack_web_client.chat_update(
            channel=channel,
            ts=event_ts,
            text=text,
            blocks=blocks if len(blocks) > 0 else None,
        )

    def _get_web_client(self, user: str) -> WebClient:
        if user == UserKind.KOBORI_AKIRA.value:
            return self.slack_user_client
        if user == UserKind.BOT_ARIKA.value:
            return self.slack_bot_client
        error_message = f"User not found. user: {user}"
        raise ValueError(error_message)
