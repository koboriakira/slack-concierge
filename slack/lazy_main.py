import logging
import os

from lazy_app import create_lazy_app

app = create_lazy_app()


def handler(event: dict, context: dict) -> None:
    """
    AWS Lambda での実行に対応するためのハンドラー関数
    """
    from slack_bolt.adapter.aws_lambda import SlackRequestHandler

    SlackRequestHandler.clear_all_log_handlers()
    print("handler is called")
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)


if __name__ == "__main__":
    # ローカルでの実行に対応するため
    if os.getenv("IS_DEBUG") == "true":
        logging.basicConfig(level=logging.DEBUG)
    app.start(port=10121)
