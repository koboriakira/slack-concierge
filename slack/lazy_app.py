import os
from slack_bolt import App
from usecase import just_ack, say_hello


def create_lazy_app() -> App:
    app = App(
        signing_secret=os.environ["SLACK_SIGNING_SECRET"],
        token=os.environ["SLACK_BOT_TOKEN"],
        process_before_response=True,
    )

    # 以下、扱える処理を羅列する

    app.message("hello")(
        ack=just_ack.execute,
        lazy=[say_hello.execute],
    )

    return app
