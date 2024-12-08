from domain.infrastructure.api.notion_api import NotionApi
from usecase.service.slack_user_client import SlackUserClient


class CreateFoodDrinkUseCase:
    def __init__(self, noton_api: NotionApi) -> None:
        self._notion_api = noton_api
        self.user_client = SlackUserClient()

    def handle(self, text: str, event_ts: str, channel: str) -> None:
        """飲食ページを作成する"""
        title = text if "\n" not in text else text.split("\n")[0]
        data = {
            "title": title,
        }
        response = self._notion_api.post(path="/food", data=data)
        self.user_client.handle(
            page_id=response["id"], channel=channel, thread_ts=event_ts
        )
