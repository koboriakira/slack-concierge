# FIXME: start_task_use_caseとstart_pomodoroで同じ処理があるので、うまく切り分けること

import logging
from datetime import date

from domain.channel import ChannelType
from slack_sdk.web import WebClient
from util.datetime import jst_now
from util.environment import Environment


class FetchDiaryMarkdownUseCase:
    def __init__(
        self,
        client: WebClient | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.client = client or WebClient(token=Environment.get_slack_bot_token())
        self.logger = logger or logging.getLogger(__name__)

    def execute(
        self,
        date_: date | None = None,
    ) -> dict[str, str]:
        if date_ is None:
            date_ = jst_now().date()
        conversations_history = self.client.conversations_history(
            channel=ChannelType.DIARY.value
        )
        messages = conversations_history["messages"]
        message = next(
            (
                message
                for message in messages
                if message["text"] == "" and len(message["files"]) == 1
            ),
            None,
        )
        file_id = message["files"][0]["id"]
        file_info = self.client.files_info(file=file_id)
        file_content = file_info["content"]
        file_download_url = file_info["url_private_download"]
        print(file_info)
        return {
            "file_content": file_content,
            "file_download_url": file_download_url,
        }


if __name__ == "__main__":
    # python -m slack.usecase.fetch_diary_markdown
    suite = FetchDiaryMarkdownUseCase()
    print(suite.execute())
