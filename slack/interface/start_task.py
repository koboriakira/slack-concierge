import logging
import json
from datetime import date as Date
from slack_sdk.web import WebClient
from slack_bolt import App, Ack
from domain_service.block.block_builder import BlockBuilder
from domain_service.view.view_builder import ViewBuilder
from domain.view.view import View
from infrastructure.api.lambda_google_calendar_api import LambdaGoogleCalendarApi
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from usecase.create_calendar import CreateCalendar as CreateCalendarUsecase
from usecase.start_task_modal import StartTaskModal as StartTaskModalUsecase
from util.logging_traceback import logging_traceback
from domain.channel.channel_type import ChannelType
from util.environment import Environment

SHORTCUT_ID = "start-task"
CALLBACK_ID = "start-task-modal"

def just_ack(ack: Ack):
    ack()

def handle_modal(ack: Ack):
    # ack() は何も渡さず呼ぶとただ今のモーダルを閉じるだけ
    # response_action とともに応答すると
    # エラーを表示したり、モーダルの内容を更新したりできる
    # https://slack.dev/bolt-python/ja-jp/concepts#view_submissions
    ack()

def start_modal_interaction(body: dict, client: WebClient):
    try:
        logging.debug(json.dumps(body, ensure_ascii=False))
        notion_api = LambdaNotionApi()
        usecase = StartTaskModalUsecase(notion_api=notion_api)
        usecase.handle(client=client, trigger_id=body["trigger_id"], callback_id=CALLBACK_ID)
    except Exception as err:
        import sys
        logging_traceback(err, sys.exc_info())


def start_task(logger: logging.Logger, view: dict, client: WebClient):
    try:
        view_model = View(view)
        state = view_model.get_state()
        task_title, task_id = state.get_static_select("task")
        logging.info(task_title)
        logging.info(task_id)
        text = f"「{task_title}」を開始します"
        channel = ChannelType.DIARY if not Environment.is_dev() else ChannelType.TEST

        client.chat_postMessage(text=text, channel=channel.value)
    except Exception as err:
        import sys
        logging_traceback(err, sys.exc_info())

def shortcut_start_task(app: App):
    app.shortcut(SHORTCUT_ID)(
        ack=just_ack,
        lazy=[start_modal_interaction],
    )

    app.view(CALLBACK_ID)(
        ack=handle_modal,
        lazy=[start_task],
    )

    return app
