import os
from slack_bolt import App
from interface.create_calendar import shortcut_create_calendar
from interface.react_user_post import message_react_user_post
from interface.sync_times import shortcut_sync_times

def create_lazy_app() -> App:
    app = App(
        signing_secret=os.environ["SLACK_SIGNING_SECRET"],
        token=os.environ["SLACK_BOT_TOKEN"],
        process_before_response=True,
    )

    # 以下、扱える処理をusecase単位で追加
    app = shortcut_create_calendar(app)
    app = message_react_user_post(app)
    app = shortcut_sync_times(app)

    return app
