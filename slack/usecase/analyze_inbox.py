import json
import logging
from datetime import date as Date

import requests
from slack_sdk.web import WebClient

from domain.infrastructure.api.notion_api import NotionApi


class AnalyzeInbox:
    def __init__(self, client: WebClient, notion_api: NotionApi, logger: logging.Logger | None = None):
        self.client = client
        self.notion_api = notion_api
        self.logger = logger or logging.getLogger(__name__)


    def handle(self, attachment: dict, channel: str, thread_ts: str) -> None:
        """ 指定したURLのページをスクレイピングしてテキストを返す """
        try:
            page_id:str = ""
            if "x.com" in attachment["original_url"]:
                page_id = self.sub_handle_twitter(attachment=attachment)
            elif "youtube.com" in attachment["original_url"]:
                self.sub_handle_youtube(attachment=attachment)
            elif "wrestle-universe.com" in attachment["original_url"]:
                page_id = self.sub_handle_wrestle_universe(attachment=attachment)
                self.notion_api.create_task(mentioned_page_id=page_id)
            else:
                self.sub_handle_default(attachment=attachment)

        except Exception:
            import sys
            import traceback
            exc_info = sys.exc_info()
            t, v, tb = exc_info
            formatted_exception = "\n".join(
                traceback.format_exception(t, v, tb))
            text=f"analyze_inbox: error ```{formatted_exception}```"
            self.client.chat_postMessage(text=text, channel=channel, thread_ts=thread_ts)

    def sub_handle_default(self, attachment: dict) -> None:
        title = attachment["title"]
        original_url = attachment["original_url"]
        cover = attachment.get("image_url")
        self.notion_api.create_webclip_page(
            url=original_url,
            title=title,
            cover=cover,
        )

    def sub_handle_twitter(self, attachment: dict) -> str:
        """ 指定したURLのページをスクレイピングしてテキストを返す(X版) """
        text = attachment["text"]
        original_url = attachment["original_url"]
        cover = attachment.get("image_url") or attachment.get("thumb_url")
        self._create_webclip_page(url=original_url, title=text, cover=cover)

    def _create_webclip_page(self, url: str, title: str, cover: str) -> dict:
        return self.notion_api.create_webclip_page(
            url=url,
            title=title,
            cover=cover,
        )

    def sub_handle_youtube(self, attachment: dict) -> None:
        """ 指定したURLの動画を登録する """
        title = attachment["title"] + " | " + attachment["author_name"]
        original_url = attachment["original_url"]
        cover = attachment.get("thumb_url")
        author_name = attachment.get("author_name")
        # FIXME: author_nameを追加して、後続の処理も実装する
        self._create_video_page(url=original_url,
                                 title=title,
                                 cover=cover,
                                 tags=[])

    def _create_video_page(self, url: str, title: str, cover: str, tags: list[str]) -> dict:
        return self.notion_api.create_video_page(
            url=url,
            title=title,
            cover=cover,
            tags=tags,
        )

    def sub_handle_wrestle_universe(self, attachment: dict) -> str:
        """ 指定したURLの動画を登録する """
        original_url:str = attachment["original_url"]
        id = original_url.split("/")[-1]
        event_url = f"https://api.wrestle-universe.com/v1/events/{id}?al=ja"
        response = requests.get(event_url)
        data:dict = response.json()
        self.logger.debug(json.dumps(data, ensure_ascii=False))
        title = data["displayName"]
        description = data["description"]
        date = Date.fromisoformat(data["labels"]["matchDate"].split("T")[0])
        cover = data["keyVisualUrl"]

        def get_promotion_name(group_key: str) -> str:
            match group_key:
                case "tjpw":
                    return "東京女子プロレス"
                case _:
                    return group_key
        promotion_name = get_promotion_name(data["labels"]["group"])
        venue = data["labels"]["venue"]
        tags = [
            promotion_name,
            venue,
        ]
        page = self.notion_api.create_prowrestling_page(
            url=original_url,
            title=title,
            date=date,
            promotion=promotion_name,
            text=description,
            tags=tags,
            cover=cover,
        )
        page_url:str = page["url"]
        self.client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=page_url,
        )
        return page["id"]



if __name__ == "__main__":
    # python -m usecase.analyze_inbox
    import os

    from infrastructure.api.lambda_notion_api import LambdaNotionApi
    logging.basicConfig(level=logging.DEBUG)
    usecase = AnalyzeInbox(
        client=WebClient(token=os.environ["SLACK_BOT_TOKEN"]),
        notion_api=LambdaNotionApi(),
        logger=logging.getLogger(__name__),
    )
    attachment = {
        "original_url": "https://www.wrestle-universe.com/ja/lives/a6LxWJxRVkMM8TqZanndgh",
    }
    usecase.handle(attachment, "C05H3USHAJU", "1706271210.390809")
