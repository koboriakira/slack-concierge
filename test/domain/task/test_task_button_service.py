from unittest import TestCase
from unittest.mock import Mock

from slack.domain.channel.thread import Thread
from slack.domain.task.task import Task
from slack.domain.task.task_button_service import TaskButtonSerivce
from slack.domain.task.task_repository import TaskRepository
from slack_sdk.web import WebClient

DUMMY_TASK_TITLE = "dummy"
DUMMY_TASK_ID = "dummy_id"
DUMMY_TASK_URL = "https://dummy.com"
DUMMY_THREAD = Thread.create(channel_id="dummy_channel_id", thread_ts="dummy_thread_ts")

class TestTaskButtonSerivce(TestCase):
    def setUp(self) -> None:
        mock_task_repository = Mock(spec=TaskRepository)
        mock_slack_client = Mock(spec=WebClient)
        self.suite = TaskButtonSerivce(task_repository=mock_task_repository, slack_client=mock_slack_client)
        return super().setUp()

    def test_正常系(self):
        # Given
        self.suite.task_repository.find_by_id.return_value = Task(
            task_id=DUMMY_TASK_ID,
            url=DUMMY_TASK_URL,
            title="dummy",
            pomodoro_count=0)

        # When
        self.suite.execute(task_page_id=DUMMY_TASK_ID, slack_thread=DUMMY_THREAD)

        # Then
        expected_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<{DUMMY_TASK_URL}|{DUMMY_TASK_TITLE}>"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "開始"
                        },
                        "style": "primary",
                        "value": DUMMY_TASK_ID,
                        "action_id": "start-pomodoro",
                    },
                ]
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
            text="",
            blocks=expected_blocks,
            channel=DUMMY_THREAD.channel_id,
            thread_ts=DUMMY_THREAD.thread_ts,
        )
