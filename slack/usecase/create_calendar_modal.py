from datetime import date as Date
from slack_sdk.web import WebClient
from domain.infrastructure.api.notion_api import NotionApi
from domain_service.block.block_builder import BlockBuilder
from domain_service.view.view_builder import ViewBuilder
import logging



class CreateCalendarModal:
    def __init__(self, notion_api: NotionApi):
        self.notion_api = notion_api

    def handle(self, client: WebClient, trigger_id: str, callback_id: str):
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

        # レシピの選択肢を作成する
        recipes = self.notion_api.list_recipes()
        recipe_options = [{
            "text": r.title,
            "value": r.id
        } for r in recipes]
        recipe_options.append({
            "text": "未定",
            "value": "_"
        })
        block_builder = block_builder.add_multi_static_select(
            action_id="dinner-recipes",
            options=recipe_options,
            optional=True,
        )

        # TODO: ふりかえりの中でつくった場合は、チャンネル・スレッドを覚える
        # block_builder = block_builder.add_context(text={
        #     "channel_id": channel_id,
        #     "thread_ts": thread_ts,
        # })

        blocks = block_builder.build()
        logging.debug(blocks)

        view = ViewBuilder(callback_id=callback_id, blocks=blocks).build()
        client.views_open(
            trigger_id=trigger_id,
            view=view,
        )
