import logging
import os
import hashlib
import hmac
import json
from slack_bolt import App, Ack, Say
from slack_sdk.web import WebClient

# 動作確認用にデバッグレベルのロギングを有効にします
# 本番運用では削除しても構いません

if  os.getenv("ENV") == "local":
    logging.basicConfig(level=logging.DEBUG)

SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

app = App(
    # リクエストの検証に必要な値
    # Settings > Basic Information > App Credentials > Signing Secret で取得可能な値
    signing_secret=SLACK_SIGNING_SECRET,
    # 上でインストールしたときに発行されたアクセストークン
    # Settings > Install App で取得可能な値
    token=SLACK_BOT_TOKEN,
    # AWS Lamdba では、必ずこの設定を true にしておく必要があります
    process_before_response=True,
)

# グローバルショットカット実行に対して、ただ ack() だけを実行する関数
# lazy に指定された関数は別の AWS Lambda 実行として非同期で実行されます
def just_ack(ack: Ack):
    ack()

# グローバルショットカット実行に対して、非同期で実行される処理
# trigger_id は数秒以内に使う必要があるが、それ以外はいくら時間がかかっても構いません
def start_modal_interaction(body: dict, client: WebClient):
    # 入力項目ひとつだけのシンプルなモーダルを開く
    client.chat_postMessage(channel=body["user"]["id"], text="Hello!")
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

# モーダルで送信ボタンが押されたときに呼び出される処理
# このメソッドは 3 秒以内に終了しなければならない
def handle_modal(ack: Ack):
    # ack() は何も渡さず呼ぶとただ今のモーダルを閉じるだけ
    # response_action とともに応答すると
    # エラーを表示したり、モーダルの内容を更新したりできる
    # https://slack.dev/bolt-python/ja-jp/concepts#view_submissions
    ack()

# モーダルで送信ボタンが押されたときに非同期で実行される処理
# モーダルの操作以外で時間のかかる処理があればこちらに書く
def handle_time_consuming_task(logger: logging.Logger, view: dict, client: WebClient):
    logger.info(view)
    # client.chat_postMessage(channel=body["user"]["id"], text="Hello!")


# @app.view のようなデコレーターでの登録ではなく
# Lazy Listener としてメインの処理を設定します
app.shortcut("run-aws-lambda-app")(
  ack=just_ack,
  lazy=[start_modal_interaction],
)
app.view("modal-id")(
  ack=handle_modal,
  lazy=[handle_time_consuming_task],
)

if __name__ == "__main__":
    # python -m concierge のように実行すると開発用 Web サーバーで起動します
    app.start(port=15000)

# これより以降は AWS Lambda 環境で実行したときのみ実行されます

from slack_bolt.adapter.aws_lambda import SlackRequestHandler

# ロギングを AWS Lambda 向けに初期化します
SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)

def verify_slack_signature(secret, timestamp, body, signature):
    return True
    # # ベースストリングの作成
    # basestring = f"v0:{timestamp}:{body}"

    # # HMAC SHA256署名の計算
    # calculated_signature = 'v0=' + hmac.new(
    #     key=bytes(secret, 'utf-8'),
    #     msg=bytes(basestring, 'utf-8'),
    #     digestmod=hashlib.sha256
    # ).hexdigest()

    # # 計算された署名と受信した署名を比較
    # return hmac.compare_digest(calculated_signature, signature)

# AWS Lambda 環境で実行される関数
def handler(event:dict, context:dict):
    logger = logging.getLogger(__name__)
    logger.info("Request event:", event)

    # headers = event['headers']
    # body = event['body']
    # slack_signature = headers.get('X-Slack-Signature')
    # slack_request_timestamp = headers.get('X-Slack-Request-Timestamp')

    # if not verify_slack_signature(SLACK_SIGNING_SECRET, slack_request_timestamp, body, slack_signature):
    #     logger.info("Invalid signature")
    #     # return {
    #     #     'statusCode': 403,
    #     #     'body': json.dumps('Invalid signature')
    #     # }
    # logger.info("Valid signature")


    # AWS Lambda 環境のリクエスト情報を app が処理できるよう変換してくれるアダプター
    slack_handler = SlackRequestHandler(app=app)
    # 応答はそのまま AWS Lambda の戻り値として返せます
    return slack_handler.handle(event, context)
