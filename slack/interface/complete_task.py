import logging
import json
from slack_sdk.web import WebClient
from slack_bolt import App, Ack
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from usecase.complete_task import CompleteTask as CompleteTaskUsecase
from util.logging_traceback import logging_traceback

ACTION_ID = "complete-task"


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
        logger.debug(json.dumps(body))
        usecase = CompleteTaskUsecase(LambdaNotionApi(), client)
        usecase.handle(notion_page_block_id, channel_id, thread_ts)
    except Exception as err:
        import sys
        logging_traceback(err, sys.exc_info())

def action_complete_task(app: App):
    app.action(ACTION_ID)(
        ack=just_ack,
        lazy=[complete_task],
    )

    return app
