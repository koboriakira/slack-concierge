import logging
from slack_sdk.web import WebClient
from openai import OpenAI
import trafilatura
from usecase.service.text_summarizer import TextSummarizer


class AnalyzeInbox:
    def __init__(self, client: WebClient, logger: logging.Logger):
        self.client = client
        self.logger = logger
        self.text_summarizer = TextSummarizer()

    def handle(self, attachments: dict):
        self.logger.info("analyze_inbox")
        self.logger.debug(attachments)
        text = attachments.get("title")
        original_url = attachments.get("original_url")
        if original_url:
            data = trafilatura.fetch_url(original_url)
            page_text = trafilatura.extract(data)
            self.text_summarizer.handle(page_text)
        # if text:
        #     use_openai(text=text)



if __name__ == "__main__":
    # python -m usecase.analyze_inbox
    import os
    logging.basicConfig(level=logging.DEBUG)
    usecase = AnalyzeInbox(
        client=WebClient(token=os.environ["SLACK_BOT_TOKEN"]),
        logger=logging.getLogger(__name__)
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
