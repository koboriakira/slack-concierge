import logging
from datetime import date as Date
from slack_sdk.web import WebClient
from slack_bolt import App, Ack
from domain_service.block.block_builder import BlockBuilder
from domain_service.view.view_builder import ViewBuilder

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

    blocks = BlockBuilder()\
      .add_datepicker(action_id="datepicker-action",
                      header="日付を選択してください",
                      placeholder="日付を選択してください",
                      initial_date=Date.today().isoformat())\
      .build()
    logging.debug(blocks)

    view = ViewBuilder(callback_id="modal-id",blocks=blocks).build()
    client.views_open(
        trigger_id=body["trigger_id"],
        view=view,
    )

def handle_time_consuming_task(logger: logging.Logger, view: dict):
    logging.info(view)

def shortcut_create_calendar(app: App):
    app.shortcut("create-calendar")(
        ack=just_ack,
        lazy=[start_modal_interaction],
    )

    app.view("modal-id")(
        ack=handle_modal,
        lazy=[handle_time_consuming_task],
    )

    return app
