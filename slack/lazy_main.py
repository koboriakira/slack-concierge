import logging
import os
from slack_bolt import App, Ack
from slack_sdk.web import WebClient

SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
app = App(
    signing_secret=SLACK_SIGNING_SECRET,
    token=SLACK_BOT_TOKEN,
    process_before_response=True,
)

logging.basicConfig(level=logging.DEBUG)


def just_ack(ack: Ack):
    """
    ただ ack() だけを実行する関数
    lazy に指定された関数は別の AWS Lambda 実行として非同期で実行されます
    """
    ack()


# def start_modal_interaction(body: dict, client: WebClient):
#     client.views_open(
#         trigger_id=body["trigger_id"],
#         view={
#             "type": "modal",
#             "callback_id": "modal-id",
#             "title": {"type": "plain_text", "text": "My App"},
#             "submit": {"type": "plain_text", "text": "Submit"},
#             "close": {"type": "plain_text", "text": "Cancel"},
#             "blocks": [
#                 {
#                     "type": "input",
#                     "element": {"type": "plain_text_input"},
#                     "label": {"type": "plain_text", "text": "Text"},
#                 },
#             ],
#         },
#     )

# def handle_modal(ack: Ack):
#     """
#     このメソッドは 3 秒以内に終了しなければならない
#     """
#     # ack() は何も渡さず呼ぶとただ今のモーダルを閉じるだけ
#     # response_action とともに応答すると
#     # エラーを表示したり、モーダルの内容を更新したりできる
#     # https://slack.dev/bolt-python/ja-jp/concepts#view_submissions
#     ack()

# def handle_time_consuming_task(logger: logging.Logger, view: dict):
#     print("handle_time_consuming_task")
#     logger.info(view)
#     print(view)


# app.shortcut("run-aws-lambda-app")(
#   ack=just_ack,
#   lazy=[start_modal_interaction],
# )

# app.view("modal-id")(
#   ack=handle_modal,
#   lazy=[handle_time_consuming_task],
# )

def say_hello(message, say):
    logging.info(message)
    user = message['user']
    say(f"Hi there, <@{user}>!")

app.message("hello")(
    ack=just_ack,
    lazy=[say_hello],
)



def handler(event, context):
    """
    AWS Lambda での実行に対応するためのハンドラー関数
    """
    from slack_bolt.adapter.aws_lambda import SlackRequestHandler

    SlackRequestHandler.clear_all_log_handlers()
    logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)

if __name__ == "__main__":
    # ローカルでの実行に対応するため
    app.start(port=10121)
