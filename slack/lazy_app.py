import os

from slack_bolt import App

from interface.complete_task import action_complete_task
from interface.create_calendar import shortcut_create_calendar
from interface.handle_message_event import handle_message_event
from interface.love_spotify_track import shortcut_love_spotify_track
from interface.react_user_post import message_react_user_post
from interface.regist import shortcut_regist
from interface.start_pomodoro import action_start_pomodoro
from interface.start_task import shortcut_start_task
from interface.sync_times import shortcut_sync_times


def create_lazy_app() -> App:
    app = App(
        signing_secret=os.environ["SLACK_SIGNING_SECRET"],
        token=os.environ["SLACK_BOT_TOKEN"],
        process_before_response=True,
    )

    # 以下、扱える処理をusecase単位で追加
    app = shortcut_create_calendar(app)
    app = shortcut_sync_times(app)
    app = shortcut_love_spotify_track(app)
    app = shortcut_regist(app)
    app = shortcut_start_task(app)
    app = action_start_pomodoro(app)
    app = action_complete_task(app)
    app = handle_message_event(app)
    app = message_react_user_post(app)

    return app  # noqa: RET504
