import os
from slack_bolt import App
from interface.create_calendar import shortcut_create_calendar

def create_lazy_app() -> App:
    app = App(
        signing_secret=os.environ["SLACK_SIGNING_SECRET"],
        token=os.environ["SLACK_BOT_TOKEN"],
        process_before_response=True,
    )

    # 以下、扱える処理をusecase単位で追加
    app = shortcut_create_calendar(app)

    return app
