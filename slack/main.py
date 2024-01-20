import logging
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.message("hello")
def message_hello(message, say):
    # イベントがトリガーされたチャンネルへ say() でメッセージを送信します
    print("message:", message)
    say(f"Hey there <@{message['user']}>!")

# AWS Lambda 環境で実行される関数
def handler(event:dict, context:dict):
    from slack_bolt.adapter.aws_lambda import SlackRequestHandler
    logger = logging.getLogger(__name__)
    logger.info("Request event:", event)
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)

# アプリを起動します
if __name__ == "__main__":
    print("Start app")
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
