from datetime import datetime
from unittest import TestCase

from slack.domain.schedule.achivement import Achievement

DUMMY_TITLE = "ダミータイトル"
DUMMY_START_DATETIME = datetime(2024, 3, 16, 11, 0, 0)
DUMMY_END_DATETIME = datetime(2024, 3, 16, 13, 0, 0)

class TestAchivement(TestCase):
    def test_正常系(self) -> None:
        # Given
        notion_url = "https://www.notion.so/xxxx"
        text = """ダミーテキスト
改行
ダミーテキスト"""
        input = f"""---
notion_url: {notion_url}
---
{text}"""

        # When
        actual = Achievement.generate(
            title=DUMMY_TITLE,
            start=DUMMY_START_DATETIME,
            end=DUMMY_END_DATETIME,
            text=input,
        )

        # Then
        self.assertEqual(actual.title, DUMMY_TITLE)
        self.assertEqual(actual.start, DUMMY_START_DATETIME)
        self.assertEqual(actual.end, DUMMY_END_DATETIME)
        self.assertEqual(actual.frontmatter["notion_url"], notion_url)
        self.assertEqual(actual.text, text)
