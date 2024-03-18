from datetime import datetime
from unittest import TestCase

import pytest
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


    @pytest.mark.learning("completeメソッドの確認")
    def test_completeメソッドの確認(self):
        # Given
        task = Task.from_title(title="ダミータイトル")

        # When
        task.complete()
        actual = task.to_dict()

        # Then
        import json
        print(json.dumps(actual, indent=2, ensure_ascii=False))
        # TypeErrorなどが出なければOK
        self.assertTrue(True)
        self.fail()
