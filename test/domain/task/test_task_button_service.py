from unittest import TestCase
from unittest.mock import Mock

from slack.domain.channel.thread import Thread
from slack.domain.task.task import Task
from slack.domain.task.task_button_service import TaskButtonSerivce
from slack_sdk.web import WebClient

DUMMY_TASK_TITLE = "dummy"
DUMMY_TASK_ID = "dummy_id"
DUMMY_TASK_URL = "https://dummy.com"
DUMMY_THREAD = Thread.create(channel_id="dummy_channel_id", thread_ts="dummy_thread_ts")

class TestTaskButtonSerivce(TestCase):
    def setUp(self) -> None:
        mock_slack_client = Mock(spec=WebClient)
        mock_slack_client.chat_postMessage.return_value = {
            "channel": "dummy_channel_id",
            "ts": "dummy_response_ts"
        }
        self.suite = TaskButtonSerivce(slack_client=mock_slack_client)
        return super().setUp()

    def test_ポモドーロの開始(self):
        # Given
        task = Task(
            task_id=DUMMY_TASK_ID,
            url=DUMMY_TASK_URL,
            title="dummy",
            pomodoro_count=0)
        # When
        _actual = self.suite.start_pomodoro(task=task, slack_thread=DUMMY_THREAD)

        # Then
        expected_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "25分のポモドーロを開始します",
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "終了"
                        },
                        "style": "danger",
                        "value": DUMMY_TASK_ID,
                        "action_id": "complete-task",
                    }
                ]
            }
        ]
        self.suite.slack_client.chat_postMessage.assert_called_once_with(
            text="25分のポモドーロを開始します",
            blocks=expected_blocks,
            channel=DUMMY_THREAD.channel_id,
            thread_ts=DUMMY_THREAD.thread_ts,
        )
