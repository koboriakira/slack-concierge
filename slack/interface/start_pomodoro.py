import json

from slack_bolt import Ack, App
from slack_sdk.web import WebClient

from domain.channel.thread import Thread
from domain.task.task_button_service import TaskButtonSerivce
from infrastructure.schedule.achievement_repository_impl import AchivementRepositoryImpl
from infrastructure.task.notion_task_repository import NotionTaskRepository
from usecase.service.event_bridge_scheduler_service import EventBridgeSchedulerService
from usecase.start_pomodoro import StartPomodoro as StartPomodoroUsecase
from util.custom_logging import get_logger
from util.error_reporter import ErrorReporter

ACTION_ID = "start-pomodoro"

logger = get_logger(__name__)

def just_ack(ack: Ack) -> None:
    ack()

def start_pomodoro(body: dict, client: WebClient) -> None:
    logger.info("start_pomodoro")
    try:
        action = body["actions"][0]
        notion_page_block_id = action["value"]

        channel_id = body["channel"]["id"]
        thread_ts = body["message"]["ts"]
        slack_thread = Thread.create(channel_id=channel_id, thread_ts=thread_ts)

        logger.debug(json.dumps(body))

        usecase = StartPomodoroUsecase(
            task_button_service=TaskButtonSerivce(slack_client=client),
            achievement_repository=AchivementRepositoryImpl(),
            task_repository=NotionTaskRepository(),
            scheduler_service=EventBridgeSchedulerService(slack_client=client),
        )

        usecase.handle(task_page_id=notion_page_block_id, slack_thread=slack_thread)
    except:  # noqa: E722
        ErrorReporter().execute()

def action_start_pomodoro(app: App) -> App:
    app.action(ACTION_ID)(
        ack=just_ack,
        lazy=[start_pomodoro],
    )
    return app
