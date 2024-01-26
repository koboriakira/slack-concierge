import logging
from datetime import date as Date
from slack_sdk.web import WebClient
from slack_bolt import App, Ack
from domain_service.block.block_builder import BlockBuilder
from domain_service.view.view_builder import ViewBuilder
from domain.view.view import View
from infrastructure.api.lambda_google_calendar_api import LambdaGoogleCalendarApi
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from usecase.daily_planning import DailyPlanning as DailyPlanningUsecase
from util.logging_traceback import logging_traceback

SHORTCUT_ID = "retrospective-daily"
CALLBACK_ID = "retrospective-daily-modal"

def just_ack(ack: Ack):
    ack()

def handle_modal(ack: Ack):
    # ack() は何も渡さず呼ぶとただ今のモーダルを閉じるだけ
    # response_action とともに応答すると
    # エラーを表示したり、モーダルの内容を更新したりできる
    # https://slack.dev/bolt-python/ja-jp/concepts#view_submissions
    ack()

def start_modal_interaction(body: dict, client: WebClient):
    logging.info("start_modal_interaction")

    try:
        today = Date.today()
        block_builder = BlockBuilder().add_datepicker(
                          action_id="date",
                          header="日付を選択してください",
                          placeholder="日付を選択してください",
                          initial_date=today.isoformat())
        blocks = block_builder.build()
        view = ViewBuilder(callback_id=CALLBACK_ID, blocks=blocks).build()
        client.views_open(
            trigger_id=body["trigger_id"],
            view=view,
        )
    except Exception as err:
        import sys
        logging_traceback(err, sys.exc_info())


def retrospective_daily(logger: logging.Logger, view: dict, client: WebClient):
    try:
        view_model = View(view)
        state = view_model.get_state()
        logging.info(state)
        context = view_model.get_context()
        logging.info(context)

        target_date = state.get_datepicker(action_id="date")

        google_calendar_api = LambdaGoogleCalendarApi()
        notion_api = LambdaNotionApi()

        daily_planning_usecase = DailyPlanningUsecase(
            google_calendar_api=google_calendar_api,
            notion_api=notion_api,
        )
        response = daily_planning_usecase.handle(target_date)
        logging.debug(response)
    except Exception as err:
        import sys
        logging_traceback(err, sys.exc_info())

def daily_planning(app: App):
    app.shortcut(SHORTCUT_ID)(
        ack=just_ack,
        lazy=[start_modal_interaction],
    )

    app.view(CALLBACK_ID)(
        ack=handle_modal,
        lazy=[retrospective_daily],
    )

    return app
