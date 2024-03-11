import logging

from slack_bolt import Ack, App
from slack_sdk.web import WebClient

from domain.view.view import State, View
from domain_service.block.block_builder import BlockBuilder
from domain_service.view.view_builder import ViewBuilder
from usecase.fetch_current_tasks_use_case import FetchCurrentTasksUseCase
from usecase.start_task_use_case import StartTaskUseCase
from util.logging_traceback import logging_traceback

SHORTCUT_ID = "start-task"
CALLBACK_ID = "start-task-modal"


class StartTaskInterface:
    def __init__(
            self,
            start_task_use_case: StartTaskUseCase) -> None:
        self.start_task_use_case = start_task_use_case

    def start_task(self, view: dict) -> None:
        try:
            view_model = View(view)
            state = view_model.get_state()
            state_task_title, state_task_id = _get_task_title_and_id(state)

            # タスクを開始する
            _ = self.start_task_use_case.execute(task_id=state_task_id, task_title=state_task_title)
        except Exception as err:
            import sys
            logging_traceback(err, sys.exc_info())

class StartTaskModalInterface:
    def __init__(
            self,
            fetch_current_tasks_use_case: FetchCurrentTasksUseCase,
            client: WebClient) -> None:
        self.fetch_current_tasks_use_case = fetch_current_tasks_use_case
        self.client = client

    def execute(self, trigger_id: str) -> None:
        try:
            task_options = self.fetch_current_tasks_use_case.execute()

            block_builder = BlockBuilder()
            if len(task_options) > 0:
                block_builder = block_builder.add_static_select(
                    action_id="task",
                    options=task_options,
                    optional=True,
                )
            block_builder = block_builder.add_plain_text_input(
                action_id="new-task",
                label="タスクを起票して開始する場合",
                optional=True,
            )
            blocks = block_builder.build()
            logging.debug("start_modal_interaction", extra=blocks)
            view = ViewBuilder(callback_id=CALLBACK_ID, blocks=blocks).build()
            self.client.views_open(
                trigger_id=trigger_id,
                view=view,
            )
        except Exception as err:
            import sys
            logging_traceback(err, sys.exc_info())


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
    fetch_current_tasks_use_case = FetchCurrentTasksUseCase()
    start_task_model_interface = StartTaskModalInterface(
        fetch_current_tasks_use_case=fetch_current_tasks_use_case,
        client=client,
    )
    start_task_model_interface.execute(trigger_id=body["trigger_id"])


def start_task(logger: logging.Logger, view: dict, client: WebClient) -> None:
    start_task_use_case = StartTaskUseCase(
        client=client,
        logger=logger,
    )
    start_task_interface = StartTaskInterface(
        start_task_use_case=start_task_use_case,
    )
    start_task_interface.start_task(view=view)


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
