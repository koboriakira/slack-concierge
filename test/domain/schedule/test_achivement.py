from datetime import datetime
from unittest import TestCase

from slack.domain.schedule.achivement import Achievement

DUMMY_TITLE = "ダミータイトル"
DUMMY_START_DATETIME = datetime(2024, 3, 16, 11, 0, 0)
DUMMY_END_DATETIME = datetime(2024, 3, 16, 13, 0, 0)

class TestAchivement(TestCase):
    def test_正常系(self):
        # Given
        input = "---\nnotion_url: https://www.notion.so/018268c8c2e241b2b3cafca6b1a6cccf\n---\n\nダミーテキスト"

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
        self.assertEqual(actual.frontmatter["notion_url"], "https://www.notion.so/018268c8c2e241b2b3cafca6b1a6cccf")
        self.assertEqual(actual.text, "ダミーテキスト")

    def test_正常系_frontmatterなし(self):
        # Given
        input = "ダミーテキスト"

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
        self.assertEqual(actual.frontmatter, {})
        self.assertEqual(actual.text, "ダミーテキスト")

    def test_正常系_frontmatterのみ(self):
        # Given
        input = "---\nnotion_url: https://www.notion.so/018268c8c2e241b2b3cafca6b1a6cccf\n---\n"

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
        self.assertEqual(actual.frontmatter["notion_url"], "https://www.notion.so/018268c8c2e241b2b3cafca6b1a6cccf")
        self.assertEqual(actual.text, "")

    def test_正常系_空(self):
        # Given
        input = ""

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
        self.assertEqual(actual.frontmatter, {})
        self.assertEqual(actual.text, "")
