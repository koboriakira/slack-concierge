import os

from slack_sdk.web import WebClient

from domain_service.block.block_builder import BlockBuilder


class AppendContextUseCase:
    def __init__(self, client: WebClient) -> None:
        self.client = client

    @staticmethod
    def get_user_client() -> "AppendContextUseCase":
        return AppendContextUseCase(client=WebClient(token=os.environ["SLACK_USER_TOKEN"]))

    @staticmethod
    def get_bot_client() -> "AppendContextUseCase":
        return AppendContextUseCase(client=WebClient(token=os.environ["SLACK_BOT_TOKEN"]))

    def execute(self, channel: str, event_ts: str, data: dict) -> None:
        messages = self.client.conversations_history(channel=channel)["messages"]
        message = next((message for message in messages if message["ts"] == event_ts), None)
        if message is None:
            error_message = f"Message not found. channel: {channel}, event_ts: {event_ts}"
            raise ValueError(error_message)

        text = message.get("text", "")
        blocks = message.get("blocks", [])
        block_builder = BlockBuilder(blocks)
        block_builder = block_builder.append_context(data)
        blocks = block_builder.build()

        import json
        print(json.dumps(blocks, ensure_ascii=False, indent=2))

        self.client.chat_update(
            channel=channel,
            ts=event_ts,
            text=text,
            blocks=blocks if len(blocks) > 0 else None,
        )
