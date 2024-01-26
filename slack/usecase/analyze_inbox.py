import logging
from slack_sdk.web import WebClient
from openai import OpenAI
from usecase.service.text_summarizer import TextSummarizer
from usecase.service.tag_analyzer import TagAnalyzer
from usecase.service.simple_scraper import SimpleScraper
from domain.infrastructure.api.notion_api import NotionApi
from util.environment import Environment
from util.logging_traceback import logging_traceback
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
            tags = self.tag_analyzer.analyze_tags(text=summary)
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
        cover = attachment.get("image_url")
        title = text[:50] # タイトルはtextの50文字目まで
        tags = self.tag_analyzer.analyze_tags(text=text)
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
        "from_url": "https://x.com/ore_meshi29/status/1718592125993152918?s=20",
        "image_url": "https://pbs.twimg.com/media/F9mqWFibEAACz8m.jpg:large",
        "image_width": 2048,
        "image_height": 1152,
        "image_bytes": 470797,
        "service_icon": "http://abs.twimg.com/favicons/twitter.3.ico",
        "id": 1,
        "original_url": "https://x.com/ore_meshi29/status/1718592125993152918?s=20",
        "fallback": "X (formerly Twitter): 俺ニキ:penguin:/コスパ最高のグルメ (@ore_meshi29) on X",
        "text": "都内のコスパ最強焼肉なら、三田『ホルモンまさる』。メニューの多くが500円前後で、美味いのに安くて会計2度見。昼から通し営業で、昼飲みしながら食べる焼肉は至福だった…:pleading_face:メモ推奨。",
        "title": "俺ニキ:penguin:/コスパ最高のグルメ (@ore_meshi29) on X",
        "title_link": "https://x.com/ore_meshi29/status/1718592125993152918?s=20",
        "service_name": "X (formerly Twitter)"
    }
    usecase.handle(attachment, "C05H3USHAJU", "1706271210.390809")
