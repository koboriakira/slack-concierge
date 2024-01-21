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
from usecase.create_calendar_modal import CreateCalendarModal as CreateCalendarModalUsecase
from util.logging_traceback import logging_traceback
from domain.channel.channel_type import ChannelType

SHORTCUT_ID = "create-calendar"
CALLBACK_ID = "create-calendar-modal"

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
        notion_api = LambdaNotionApi()
        usecase = CreateCalendarModalUsecase(notion_api=notion_api)
        usecase.handle(client=client, trigger_id=body["trigger_id"], callback_id=CALLBACK_ID)
    except Exception as err:
        import sys
        logging_traceback(err, sys.exc_info())


def create_calendar(logger: logging.Logger, view: dict, client: WebClient):
    try:
        view_model = View(view)
        state = view_model.get_state()
        logging.info(state)
        context = view_model.get_context()
        logging.info(context)

        is_morning_childcare = state.is_checked(
            action_id="childcare-action", value="is_morning_childcare")
        is_evening_childcare = state.is_checked(
            action_id="childcare-action", value="is_evening_childcare")
        is_weekly_review = state.is_checked(
            action_id="weekly-review-action", value="is_weekly_review")
        is_cook_dinner = state.is_checked(
            action_id="meal-action", value="is_cook_dinner")
        wakeup_time = state.get_timepicker(
            action_id="wakeup-time")
        lunch_time = state.get_timepicker(
            action_id="lunch-time")
        dinner_time = state.get_timepicker(
            action_id="dinner-time")
        breakfast_detail = state.get_text_input_value(
            action_id="breakfast_detail")
        lunch_detail = state.get_text_input_value(
            action_id="lunch_detail")
        dinner_recipes = state.get_multi_selected(
            action_id="dinner-recipes")
        dinner_recipe_ids = [r["value"] for r in dinner_recipes]
        date = state.get_datepicker(
            action_id="datepicker-action")
        chennel_id = context.channel_id or ChannelType.NOTIFICATION.value
        thread_ts = context.thread_ts if context.channel_id else None

        google_calendar_api = LambdaGoogleCalendarApi()
        notion_api = LambdaNotionApi()

        # FIXME: 実処理
        create_calendar_usecase = CreateCalendarUsecase(
            is_morning_childcare=is_morning_childcare,
            is_evening_childcare=is_evening_childcare,
            is_weekly_review=is_weekly_review,
            is_cook_dinner=is_cook_dinner,
            wakeup_time=wakeup_time,
            lunch_time=lunch_time,
            dinner_time=dinner_time,
            breakfast_detail=breakfast_detail,
            lunch_detail=lunch_detail,
            dinner_recipe_ids=dinner_recipe_ids,
            date=date,
            google_calendar_api=google_calendar_api,
            notion_api=notion_api,
        )
        response = create_calendar_usecase.handle()
        logging.debug(response)

        client.chat_postMessage(
            text=response, channel=chennel_id, thread_ts=thread_ts)
    except Exception as err:
        import sys
        logging_traceback(err, sys.exc_info())

def shortcut_create_calendar(app: App):
    app.shortcut(SHORTCUT_ID)(
        ack=just_ack,
        lazy=[start_modal_interaction],
    )

    app.view(CALLBACK_ID)(
        ack=handle_modal,
        lazy=[create_calendar],
    )

    return app
