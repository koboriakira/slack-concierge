import logging
import os

from slack_bolt import Ack, App
from slack_sdk.web import WebClient

from usecase.service.sqs_service import SqsService
from util.error_reporter import ErrorReporter

ACTION_ID = "complete-task"
AWS_ACCOUNT_ID = os.environ["AWS_ACCOUNT_ID"]
QUEUE_URL = f"https://sqs.ap-northeast-1.amazonaws.com/{AWS_ACCOUNT_ID}/SlackConcierge-CompleteTaskQueue31F46268-1zWLUVzSO2Bj"


def just_ack(ack: Ack):
    ack()


def complete_task(body: dict, client: WebClient, logger:logging.Logger):
    logger.info("complete_task")
    try:
        # ボタンに埋め込まれたvalueを取得。これがtrack_idになる
        action = body["actions"][0]
        notion_page_block_id = action["value"]

        # 返信用にchannel_id、thread_tsを取得
        channel_id = body["channel"]["id"]
        thread_ts = body["message"]["ts"]

        # タスク完了を返信
        client.chat_postMessage(text="タスクを完了しました！", channel=channel_id, thread_ts=thread_ts)

        # SQSにメッセージを送信
        sqs_service = SqsService()
        sqs_service.send(QUEUE_URL, {
            "page_id": notion_page_block_id,
            "channel": channel_id,
            "thread_ts": thread_ts,
        })
    except:  # noqa: E722
        ErrorReporter().execute()

def action_complete_task(app: App):
    app.action(ACTION_ID)(
        ack=just_ack,
        lazy=[complete_task],
    )

    return app
