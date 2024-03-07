import logging
import os
import unittest
from unittest.mock import Mock

from slack.infrastructure.api.lambda_notion_api import LambdaNotionApi
from slack.usecase.analyze_inbox import AnalyzeInbox
from slack_sdk.web import WebClient


class TestAnalyzeInbox(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG),
        self.analyze_inbox = AnalyzeInbox(
            client=WebClient(token=os.environ["SLACK_BOT_TOKEN"]),
            logger=logging.getLogger(__name__),
            notion_api=Mock(LambdaNotionApi),
            # is_debug=True
        )

    def test_sub_handle_twitter(self):
        attachment = {
          "from_url": "https://www.youtube.com/watch?v=TPJkNq88wBM",
          "thumb_url": "https://i.ytimg.com/vi/TPJkNq88wBM/hqdefault.jpg",
          "thumb_width": 480,
          "thumb_height": 360,
          "video_html": '<iframe width="400" height="225" src="https://www.youtube.com/embed/TPJkNq88wBM?feature=oembed&autoplay=1&iv_load_policy=3" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen title="今年最後の質問コーナーだ！！みんな！観て‼︎!"></iframe>',
          "video_html_width": 400,
          "video_html_height": 225,
          "service_icon": "https://a.slack-edge.com/80588/img/unfurl_icons/youtube.png",
          "id": 1,
          "original_url": "https://www.youtube.com/watch?v=TPJkNq88wBM",
          "fallback": "YouTube Video: 今年最後の質問コーナーだ！！みんな！観て‼︎!",
          "title": "今年最後の質問コーナーだ！！みんな！観て‼︎!",
          "title_link": "https://www.youtube.com/watch?v=TPJkNq88wBM",
          "author_name": "ヘアピンまみれ Hairpin Mamire",
          "author_link": "https://www.youtube.com/@hairpin_mamire",
          "service_name": "YouTube",
          "service_url": "https://www.youtube.com/",
        }
        channel = "C05H3USHAJU"
        thread_ts = "1707452514.914669"

        result = self.analyze_inbox.handle(attachment, channel, thread_ts)
        print(result)
        self.assertIsNotNone(result)
