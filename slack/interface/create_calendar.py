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
from util.logging_traceback import logging_traceback

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

    today = Date.today()

    block_builder = BlockBuilder().add_datepicker(
                      action_id="datepicker-action",
                      header="日付を選択してください",
                      placeholder="日付を選択してください",
                      initial_date=today.isoformat())

    # 土曜もしくは日曜の場合は、週次レビューの有無を聞く
    if today.weekday() in [5, 6]:
        block_builder = block_builder.add_checkboxes(
            action_id="weekly-review-action",
            header="週次レビューはやりますか？",
            options=[
                {
                    "text": "やる",
                    "value": "is_weekly_review"
                },
            ]
        )

    block_builder = block_builder.add_checkboxes(
            action_id="childcare-action",
            header="明日の子育ての予定を選択してください。",
            options=[
                {
                    "text": "朝の子育て",
                    "value": "is_morning_childcare"
                },
                {
                    "text": "夜の子育て",
                    "value": "is_evening_childcare"
                }
            ]
        )
    block_builder = block_builder.add_checkboxes(
        action_id="meal-action",
        header="夕食はつくりますか？",
        options=[
            {
                "text": "夕食を作る",
                "value": "is_cook_dinner"
            }
        ]
    )
    block_builder = block_builder.add_timepicker(
        action_id="wakeup-time",
        placeholder="起床の時間を選択してください",
        initial_time="07:00",
        label="起床の時間"
    )
    block_builder = block_builder.add_plain_text_input(
        action_id="breakfast_detail",
        label="朝食の予定",
        multiline=True,
        optional=True,
    )
    block_builder = block_builder.add_timepicker(
        action_id="lunch-time",
        placeholder="昼食の時間を選択してください",
        initial_time="12:00",
        label="昼食の時間"
    )
    block_builder = block_builder.add_plain_text_input(
        action_id="lunch_detail",
        label="昼食の予定",
        multiline=True,
        optional=True,
    )
    block_builder = block_builder.add_timepicker(
        action_id="dinner-time",
        placeholder="夕食の時間を選択してください",
        initial_time="18:30",
        label="夕食の時間"
    )

    # FIXME: レシピ取得
    # block_builder = block_builder.add_multi_static_select(
    #     action_id="dinner-recipes",
    #     options=recipe_options,
    #     optional=True,
    # )

    # FIXME: チャンネル、スレッド
    # block_builder = block_builder.add_context(text={
    #     "channel_id": channel_id,
    #     "thread_ts": thread_ts
    # })

    blocks = block_builder.build()
    logging.debug(blocks)

    view = ViewBuilder(callback_id="modal-id",blocks=blocks).build()
    client.views_open(
        trigger_id=body["trigger_id"],
        view=view,
    )

def create_calendar(logger: logging.Logger, view: dict):
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
        date = state.get_datepicker(
            action_id="datepicker-action")

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
            dinner_recipes=dinner_recipes,
            # primary_projects=primary_projects,
            date=date,
            google_calendar_api=google_calendar_api,
            notion_api=notion_api,
        )
        response = create_calendar_usecase.handle()
        logging.debug(response)

        # self.slack_bot_api.chat_post_message(
        #     text=response, channel_id=request.channel_id, thread_ts=request.thread_ts)
    except Exception as err:
        import sys
        exc_info=sys.exc_info()

        logging_traceback(err, exc_info)

def shortcut_create_calendar(app: App):
    app.shortcut("create-calendar")(
        ack=just_ack,
        lazy=[start_modal_interaction],
    )

    app.view("modal-id")(
        ack=handle_modal,
        lazy=[create_calendar],
    )

    return app
