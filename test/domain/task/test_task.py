from datetime import datetime
from unittest import TestCase

from slack.domain.task.task import Task
from slack.util.datetime import JST


class TestTask(TestCase):
    def test_json化できるようなdictに変換する(self):
        # Given
        task = Task(
            title="ダミータイトル",
            is_routine=True,
            description="ダミーディスクリプション",
            pomodoro_count=3,
            status="ダミーステータス",
            start_date=datetime(2024, 3, 16, 11, 0, 0, tzinfo=JST),
            end_date=datetime(2024, 3, 16, 13, 0, 0, tzinfo=JST),
            task_id="ダミータスクID",
            url="ダミーURL",
            mentioned_page_id="ダミーメンションID",
        )

        # When
        actual = task.to_dict()

        # Then
        self.assertEqual(actual, {
            "title": "ダミータイトル",
            "is_routine": True,
            "description": "ダミーディスクリプション",
            "pomodoro_count": 3,
            "status": "ダミーステータス",
            "start_date": "2024-03-16T11:00:00+09:00",
            "end_date": "2024-03-16T13:00:00+09:00",
            "task_id": "ダミータスクID",
            "url": "ダミーURL",
            "mentioned_page_id": "ダミーメンションID",
        })
