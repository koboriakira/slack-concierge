import json
import logging

from domain.channel import ChannelType
from domain.event_scheduler.pomodoro_timer_request import PomodoroTimerRequest
from domain.view.view import State, View
from infrastructure.api.lambda_google_calendar_api import LambdaGoogleCalendarApi
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from slack_bolt import Ack, App
from slack_sdk.web import WebClient
from usecase.start_pomodoro import StartPomodoro as StartPomodoroUsecase
from usecase.start_task import StartTask as StartTaskUsecase
from util.environment import Environment
from util.logging_traceback import logging_traceback

SHORTCUT_ID = "start-task"
CALLBACK_ID = "start-task-modal"

class TaskTitleNotFoundError(ValueError):
    def __init__(self) -> None:
        super().__init__("task_title が取得できませんでした")


def just_ack(ack: Ack) -> None:
    ack()

def handle_modal(ack: Ack) -> None:
    # ack() は何も渡さず呼ぶとただ今のモーダルを閉じるだけ
    # response_action とともに応答すると
    # エラーを表示したり、モーダルの内容を更新したりできる
    # https://slack.dev/bolt-python/ja-jp/concepts#view_submissions
    ack()

def start_modal_interaction(body: dict, client: WebClient) -> None:
    try:
        logging.debug(json.dumps(body, ensure_ascii=False))
        notion_api = LambdaNotionApi()
        usecase = StartTaskUsecase(notion_api=notion_api, client=client)
        usecase.handle_modal(client=client, trigger_id=body["trigger_id"], callback_id=CALLBACK_ID)
    except Exception as err:
        import sys
        logging_traceback(err, sys.exc_info())


def start_task(logger: logging.Logger, view: dict, client: WebClient) -> None:
    try:
        notion_api = LambdaNotionApi()
        usecase = StartTaskUsecase(notion_api=notion_api, client=client)
        view_model = View(view)
        state = view_model.get_state()

        task_title, task_id = _get_task_title_and_id(state)
        response = usecase.handle_prepare(task_id=task_id, task_title=task_title)
        thread_ts = response["thread_ts"]
        page_id = response["page_id"]

        channel = ChannelType.DIARY if not Environment.is_dev() else ChannelType.TEST

        start_pomodoro = StartPomodoroUsecase(notion_api=notion_api, google_api=LambdaGoogleCalendarApi(), client=client)
        event_scheduler_request = PomodoroTimerRequest(
            page_id=page_id,
            channel=channel.value,
            thread_ts=thread_ts,
        )
        start_pomodoro.handle(request=event_scheduler_request)
    except Exception as err:
        import sys
        logging_traceback(err, sys.exc_info())

def _get_task_title_and_id(state: State) -> tuple[str, str | None]:
        if (task := state.get_static_select("task")) is not None:
            # 既存タスクから選んだ場合
            return task
        elif (new_task_title := state.get_text_input_value("new-task")) is not None:
            # 新規タスクを起票した場合
            return new_task_title, None
        elif (routine_task := state.get_static_select("routine-task")) is not None:
            # ルーチンタスクを選択した場合
            task_title, _ = routine_task
            return f"{task_title}【ルーティン】", None
        raise TaskTitleNotFoundError

def shortcut_start_task(app: App) -> App:
    app.shortcut(SHORTCUT_ID)(
        ack=just_ack,
        lazy=[start_modal_interaction],
    )

    app.view(CALLBACK_ID)(
        ack=handle_modal,
        lazy=[start_task],
    )

    return app
