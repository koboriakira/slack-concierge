import logging
from lazy_app import create_lazy_app

app = create_lazy_app()


def handler(event, context):
    """
    AWS Lambda での実行に対応するためのハンドラー関数
    """
    headers: dict = event.get("headers", {})
    if headers.get("x-slack-bolt-lazy-only") is not None:
        # レイジーモードの場合は、ハンドラーを呼び出さない
        # この分岐を入れないと、一度のリクエストで複数回のレスポンスが返されてしまう
        return {}
    from slack_bolt.adapter.aws_lambda import SlackRequestHandler

    SlackRequestHandler.clear_all_log_handlers()
    print("handler is called")
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)


if __name__ == "__main__":
    # ローカルでの実行に対応するため
    logging.basicConfig(level=logging.DEBUG)
    app.start(port=10121)
