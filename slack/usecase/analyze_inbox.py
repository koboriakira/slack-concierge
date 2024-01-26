import logging
from slack_sdk.web import WebClient
from datetime import date as Date
import requests
from usecase.service.text_summarizer import TextSummarizer
from usecase.service.tag_analyzer import TagAnalyzer
from usecase.service.simple_scraper import SimpleScraper
from domain.infrastructure.api.notion_api import NotionApi
import json

class AnalyzeInbox:
    def __init__(self, client: WebClient, logger: logging.Logger, notion_api: NotionApi):
        self.client = client
        self.logger = logger
        self.notion_api = notion_api
        self.text_summarizer = TextSummarizer(logger=logger)
        self.tag_analyzer = TagAnalyzer()
        self.simple_scraper = SimpleScraper()

    def handle(self, attachment: dict, channel: str, thread_ts: str) -> None:
        """ 指定したURLのページをスクレイピングしてテキストを返す """
        try:
            if "x.com" in attachment["original_url"]:
                return self.handle_twitter(attachment=attachment, channel=channel, thread_ts=thread_ts)

            if "youtube.com" in attachment["original_url"]:
                return self.handle_youtube(attachment=attachment, channel=channel, thread_ts=thread_ts)

            if "wrestle-universe.com" in attachment["original_url"]:
                return self.handle_wrestle_universe(attachment=attachment, channel=channel, thread_ts=thread_ts)


            self._post_progress_if_dev(text=f"analyze_inbox: start ```{json.dumps(attachment)}", channel=channel, thread_ts=thread_ts)
            title = attachment["title"]
            original_url = attachment["original_url"]
            cover = attachment.get("image_url")
            page_text, formatted_page_text = self.simple_scraper.handle(url=original_url)
            if page_text is None:
                raise Exception("ページのスクレイピングに失敗しました。")
            self.logger.debug(page_text)
            summary = self.text_summarizer.handle(page_text)
            self.logger.debug(summary)
            self._post_progress_if_dev(text=f"analyze_inbox: summary ```{summary}```", channel=channel, thread_ts=thread_ts)
            tags = self.tag_analyzer.handle(text=summary)
            self._post_progress_if_dev(text=f"analyze_inbox: tags ```{tags}```", channel=channel, thread_ts=thread_ts)

            self._post_progress_if_dev(text=f"create_webclip_page: ```{original_url}\n{title}\n{summary}\n{tags}\n{page_text}\n{attachment.get('image_url')}````", channel=channel, thread_ts=thread_ts)
            page = self.notion_api.create_webclip_page(
                url=original_url,
                title=title,
                summary=summary,
                tags=tags,
                text=formatted_page_text,
                cover=cover,
            )
            self._post_progress_if_dev(text=f"analyze_inbox: page ```{page}```", channel=channel, thread_ts=thread_ts)
            page_url:str = page["url"]
            result_text = f"{page_url}\n\n```{summary}```"
            self.client.chat_postMessage(
                channel=channel,
                thread_ts=thread_ts,
                text=result_text,
            )
        except Exception as e:
            import sys
            import traceback
            exc_info = sys.exc_info()
            t, v, tb = exc_info
            formatted_exception = "\n".join(
                traceback.format_exception(t, v, tb))
            self._post_progress_if_dev(text=f"analyze_inbox: error ```{formatted_exception}```", channel=channel, thread_ts=thread_ts)

    def handle_twitter(self, attachment: dict, channel: str, thread_ts: str) -> None:
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

    def handle_youtube(self, attachment: dict, channel: str, thread_ts: str) -> None:
        """ 指定したURLの動画を登録する """
        title = attachment["title"] + " | " + attachment["author_name"]
        original_url = attachment["original_url"]
        cover = attachment.get("thumb_url")
        tags = self.tag_analyzer.handle(text=title)
        page = self.notion_api.create_video_page(
            url=original_url,
            title=title,
            tags=tags,
            cover=cover,
        )
        page_url:str = page["url"]
        self.client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=page_url,
        )

    def handle_wrestle_universe(self, attachment: dict, channel: str, thread_ts: str) -> None:
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
        tags = self.tag_analyzer.handle_for_prowrestling(text=description)
        tags.append(promotion_name)
        tags.append(venue)
        page = self.notion_api.create_prowrestling_page(
            url=original_url,
            title=title,
            date=date,
            promotion=promotion_name,
            tags=tags,
            cover=cover,
        )
        page_url:str = page["url"]
        self.client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=page_url,
        )


    def _post_progress_if_dev(self, text: str, channel: str, thread_ts: str):
        # if Environment.is_dev():
        self.client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=text,
        )

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
