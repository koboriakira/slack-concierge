import logging
from slack_sdk.web import WebClient
from openai import OpenAI
from usecase.service.text_summarizer import TextSummarizer
from usecase.service.tag_analyzer import TagAnalyzer
from usecase.service.simple_scraper import SimpleScraper
from domain.infrastructure.api.notion_api import NotionApi
from util.environment import Environment

class AnalyzeInbox:
    def __init__(self, client: WebClient, logger: logging.Logger, notion_api: NotionApi):
        self.client = client
        self.logger = logger
        self.notion_api = notion_api
        self.text_summarizer = TextSummarizer(logger=logger)
        self.tag_analyzer = TagAnalyzer()
        self.simple_scraper = SimpleScraper()

    def handle(self, attachments: dict, channel: str, thread_ts: str) -> None:
        self._post_progress_if_dev(text="analyze_inbox: start", channel=channel, thread_ts=thread_ts)
        title = attachments["title"]
        original_url = attachments["original_url"]
        page_text = self.simple_scraper.handle(url=original_url)
        if page_text is None:
            raise Exception("ページのスクレイピングに失敗しました。")
        self.logger.debug(page_text)
        summary = self.text_summarizer.handle(page_text)
        self.logger.debug(summary)
        self._post_progress_if_dev(text=f"analyze_inbox: summary ```{summary}```", channel=channel, thread_ts=thread_ts)
        tags = self.tag_analyzer.analyze_tags(text=summary)
        self.logger.debug(tags)
        self._post_progress_if_dev(text=f"analyze_inbox: tags ```{tags}```", channel=channel, thread_ts=thread_ts)

        self.logger.info("create_webclip_page")
        page = self.notion_api.create_webclip_page(
            url=original_url,
            title=title,
            summary=summary,
            tags=tags,
            text=page_text,
            cover=attachments.get("image_url"),
        )
        page_url:str = page["url"]
        result_text = f"{page_url}\n\n```{summary}```"
        self.client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=result_text,
        )


    def _post_progress_if_dev(self, text: str, channel: str, thread_ts: str):
        if Environment.is_dev():
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
        "image_url": "https://assets.st-note.com/production/uploads/images/126014735/rectangle_large_type_2_a12108f8a67248cc00e888924d6a08dc.jpeg?fit=bounds&quality=85&width=1280",
        "image_width": 1280,
        "image_height": 670,
        "image_bytes": 133563,
        "from_url": "https://note.com/koboriakira/n/ne14eaa1c50d2?sub_rt=share_pb",
        "service_icon": "https://assets.st-note.com/poc-image/manual/note-common-images/production/icons/apple-touch-icon.png",
        "id": 1,
        "original_url": "https://note.com/koboriakira/n/ne14eaa1c50d2?sub_rt=share_pb",
        "fallback": "note（ノート）: 東京女子プロレスのベストバウト29選 (2023)｜コボリアキラ",
        "text": "（写真は&amp;nbsp;東京女子プロレス誕生10周年記念興行～We are TJPW～ | DDTプロレスリング公式サイト&amp;nbsp;より） 東京女子プロレスより、2023年ベストバウトの募集がありました。 今年もあなたが選ぶ2023年TJPWベストバウトを募集します！ 今年の #TJPW の試合であなたが思うベストバウトを1〜3位まで順位をつけてX(旧Twitter)に投稿してください！ 1位3点、2位2点、3位1点で集計します。 投票期間は12月31日23時59分までです。#tjpwBB23 のハッシュタグを必ずお願いします！ <http://pic.twitter.com/opOYbR|pic.twitter.com/opOYbR>",
        "title": "東京女子プロレスのベストバウト29選 (2023)｜コボリアキラ",
        "title_link": "https://note.com/koboriakira/n/ne14eaa1c50d2?sub_rt=share_pb",
        "service_name": "note（ノート）"
      }
    usecase.handle(attachment)
