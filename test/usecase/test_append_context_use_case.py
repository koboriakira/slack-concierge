import json
import logging
import os
import unittest

from slack.usecase.append_context_use_case import AppendContextUseCase
from slack_sdk.web import WebClient

CHANNEL_TEST = "C05H3USHAJU"
SAMPLE_TEXT = "TestAnalyzeWebpageUseCase"
SAMPLE_PAGE_ID = "12345"
SAMPLE_DATA = {"page_id": SAMPLE_PAGE_ID}

class TestAnalyzeWebpageUseCase(unittest.TestCase):
    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG)

        # 実際にSlack投稿しながらテストしてみる
        self.client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        self.suite = AppendContextUseCase.get_bot_client()

    def tearDown(self) -> None:
        self._delete_message()
        return super().tearDown()

    def test_対象の投稿が見つからなければ例外を投げる(self) -> None:
        with self.assertRaises(ValueError):
            self.suite.execute(channel=CHANNEL_TEST, event_ts="1710342408.000000", data=SAMPLE_DATA)

    def test_contextが存在しない投稿に追加する(self) -> None:
        # Given
        event_ts = self._chat_postMessage(text=SAMPLE_TEXT)

        # When
        self.suite.execute(channel=CHANNEL_TEST, event_ts=event_ts, data=SAMPLE_DATA)

        # Then
        self._assert_text_and_context(event_ts=event_ts, expected_text=SAMPLE_TEXT, expected_context=SAMPLE_DATA)

    def test_contextが存在する投稿に追加する(self) -> None:
        # Given
        previous_data = {"previous": "data"}
        event_ts = self._chat_postMessage(text=SAMPLE_TEXT, data=previous_data)

        # When
        self.suite.execute(channel=CHANNEL_TEST, event_ts=event_ts, data=SAMPLE_DATA)

        # Then
        expected_context = {
            **previous_data,
            **SAMPLE_DATA,
        }
        self._assert_text_and_context(event_ts=event_ts, expected_text=SAMPLE_TEXT, expected_context=expected_context)

    def _assert_text_and_context(self, event_ts: str, expected_text: str, expected_context: dict) -> None:
        messages = self.client.conversations_history(channel=CHANNEL_TEST)["messages"]
        message = next((message for message in messages if message["ts"] == event_ts), None)
        self.assertIsNotNone(message)
        blocks = message["blocks"]
        self.assertIsNotNone(blocks)

        # textを検証する
        self.assertEqual(message["text"], expected_text)

        # contextを検証する
        context_blocks = [block for block in blocks if block["type"] == "context"]
        self.assertIsNotNone(context_blocks)
        self.assertEqual(len(context_blocks), 1)
        context_block = context_blocks[0]
        elements = context_block["elements"]
        self.assertIsNotNone(elements)
        self.assertEqual(len(elements), 1)
        element = elements[0]
        self.assertEqual(element["type"], "plain_text")
        self.assertEqual(json.loads(element["text"]), expected_context)

    def _chat_postMessage(self, text: str|None = None, data: dict|None = None) -> str:
        """ メッセージを投稿し、投稿したメッセージのtsを返す"""
        text = text or SAMPLE_TEXT
        self._delete_message(text=text)

        if not data:
            response = self.client.chat_postMessage(channel=CHANNEL_TEST, text=text)
            return response["ts"]
        blocks = [{
            "type": "context",
            "elements": [
                {
                    "type": "plain_text",
                    "text": json.dumps(data, ensure_ascii=False)
                }
            ]
        }]
        response = self.client.chat_postMessage(channel=CHANNEL_TEST, text=text, blocks=blocks)
        return response["ts"]

    def _delete_message(self, text: str|None = None) -> None:
        text = text or SAMPLE_TEXT
        messages = self.client.conversations_history(channel=CHANNEL_TEST)["messages"]
        for message in messages:
            if message.get("text") == text:
                self.client.chat_delete(channel=CHANNEL_TEST, ts=message["ts"])
