import json
import logging
from slack_sdk.web import WebClient
from datetime import date as Date
import requests
from usecase.service.text_summarizer import TextSummarizer
from usecase.service.tag_analyzer import TagAnalyzer
from usecase.service.simple_scraper import SimpleScraper
from domain.infrastructure.api.notion_api import NotionApi

class AnalyzeInbox:
    def __init__(self, client: WebClient, logger: logging.Logger, notion_api: NotionApi, is_debug: bool = False):
        self.client = client
        self.logger = logger
        self.notion_api = notion_api
        self.text_summarizer = TextSummarizer(logger=logger, is_debug=is_debug)
        self.tag_analyzer = TagAnalyzer(is_debug=is_debug)
        self.simple_scraper = SimpleScraper()

    def handle(self, attachment: dict, channel: str, thread_ts: str) -> str:
        """ 指定したURLのページをスクレイピングしてテキストを返す """
        try:
            page_id:str = ""
            if "x.com" in attachment["original_url"]:
                page_id = self.sub_handle_twitter(attachment=attachment, channel=channel, thread_ts=thread_ts)
                self.notion_api.create_task(mentioned_page_id=page_id)
            elif "youtube.com" in attachment["original_url"]:
                self.sub_handle_youtube(attachment=attachment, channel=channel, thread_ts=thread_ts)
            elif "wrestle-universe.com" in attachment["original_url"]:
                page_id = self.sub_handle_wrestle_universe(attachment=attachment, channel=channel, thread_ts=thread_ts)
                self.notion_api.create_task(mentioned_page_id=page_id)
            else:
                self.sub_handle_default(attachment=attachment, channel=channel, thread_ts=thread_ts)


        except Exception as e:
            import sys
            import traceback
            exc_info = sys.exc_info()
            t, v, tb = exc_info
            formatted_exception = "\n".join(
                traceback.format_exception(t, v, tb))
            self.client.chat_postMessage(text=f"analyze_inbox: error ```{formatted_exception}```", channel=channel, thread_ts=thread_ts)

    def sub_handle_default(self, attachment: dict, channel: str, thread_ts: str) -> None:
        title = attachment["title"]
        original_url = attachment["original_url"]
        cover = attachment.get("image_url")
        self.notion_api.create_webclip_page(
            url=original_url,
            title=title,
            cover=cover,
        )

    def sub_handle_twitter(self, attachment: dict, channel: str, thread_ts: str) -> str:
        """ 指定したURLのページをスクレイピングしてテキストを返す(X版) """
        text = attachment["text"]
        original_url = attachment["original_url"]
        cover = attachment.get("image_url") or attachment.get("thumb_url")
        title = text[:50] # タイトルはtextの50文字目まで
        tags = self.tag_analyzer.handle(text=text)
        page = self.notion_api.create_webclip_page(
            url=original_url,
            title=title,
            summary=text,
            tags=tags,
            text=text,
            cover=cover,
        )
        page_url:str = page["url"]
        self.client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=page_url,
        )

    def sub_handle_youtube(self, attachment: dict, channel: str, thread_ts: str) -> None:
        """ 指定したURLの動画を登録する """
        title = attachment["title"] + " | " + attachment["author_name"]
        original_url = attachment["original_url"]
        cover = attachment.get("thumb_url")
        tags = self.tag_analyzer.handle(text=title)
        tags.append(attachment["author_name"])
        self.notion_api.create_video_page(
            url=original_url,
            title=title,
            tags=tags,
            cover=cover,
        )

    def sub_handle_wrestle_universe(self, attachment: dict, channel: str, thread_ts: str) -> str:
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


    def _post_progress_if_dev(self, text: str, channel: str, thread_ts: str):
        pass
        # if Environment.is_dev():
        #     self.client.chat_postMessage(
        #         channel=channel,
        #         thread_ts=thread_ts,
        #         text=text,
        #     )

if __name__ == "__main__":
    # python -m usecase.analyze_inbox
    import os
    from infrastructure.api.lambda_notion_api import LambdaNotionApi
    logging.basicConfig(level=logging.DEBUG)
    usecase = AnalyzeInbox(
        client=WebClient(token=os.environ["SLACK_BOT_TOKEN"]),
        logger=logging.getLogger(__name__),
        notion_api=LambdaNotionApi(),
    )
    attachment = {
        "original_url": "https://www.wrestle-universe.com/ja/lives/a6LxWJxRVkMM8TqZanndgh",
    }
    usecase.handle(attachment, "C05H3USHAJU", "1706271210.390809")
