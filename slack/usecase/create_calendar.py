import logging
from slack_sdk.web import WebClient
from slack_bolt import App, Ack


def shortcut_create_calendar(app: App):
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
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "modal-id",
                "title": {"type": "plain_text", "text": "My App"},
                "submit": {"type": "plain_text", "text": "Submit"},
                "close": {"type": "plain_text", "text": "Cancel"},
                "blocks": [
                    {
                        "type": "input",
                        "element": {"type": "plain_text_input"},
                        "label": {"type": "plain_text", "text": "Text"},
                    },
                ],
            },
        )

    def handle_time_consuming_task(logger: logging.Logger, view: dict):
        logging.info(view)

    app.shortcut("create-calendar")(
        ack=just_ack,
        lazy=[start_modal_interaction],
    )

    app.view("modal-id")(
        ack=handle_modal,
        lazy=[handle_time_consuming_task],
    )

    return app
