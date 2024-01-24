import os
import json
import logging
from slack_sdk.web import WebClient
from datetime import datetime as Datetime
from datetime import timedelta
from domain.schedule.schedule import Schedule
from infrastructure.api.lambda_google_calendar_api import LambdaGoogleCalendarApi
from domain_service.block.block_builder import BlockBuilder
from domain.user.user_kind import UserKind
from domain.channel.channel_type import ChannelType

# 5分先にする
NOW = Datetime.now() + timedelta(minutes=5)
# NOW = Datetime(2024, 1, 22, 12, 0)
IS_TEST = False

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_BOT = WebClient(token=SLACK_BOT_TOKEN)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if os.environ.get("ENVIRONMENT") == "dev":
    logger.setLevel(logging.DEBUG)


google_calendar_api = LambdaGoogleCalendarApi()
cache = None

def handler(event, context):
    """
    AWS Lambda での実行に対応するハンドラー関数
    """
    global cache

    data = google_calendar_api.get_current_schedules()
    if data is None:
        return data

    schedules = [Schedule.from_entity(d) for d in data]
    for schedule in schedules:
        post_schedule(schedule)
    return schedules

def post_schedule(schedule: Schedule, is_debug:bool = False) -> None:
    block_builder = BlockBuilder()
    user_mention = UserKind.KOBORI_AKIRA.mention()
    schedule_memo = "\n".join(schedule.get_memo())
    block_builder = block_builder.add_mrkdwn_section(
        text=f"{user_mention}\n{schedule.title}を開始しましょう！\n{schedule_memo}")
    block_builder = block_builder.add_divider()
    block_builder = block_builder.add_timepicker(action_id="start-time",
                                                 placeholder="開始",
                                                 label="開始",
                                                 initial_time=schedule.start.strftime("%H:%M"))
    block_builder = block_builder.add_timepicker(action_id="end-time",
                                                 placeholder="開始",
                                                 label="終了",
                                                 initial_time=schedule.end.strftime("%H:%M"))
    sub_task_options = []
    for sub_task in schedule.sub_tasks:
        sub_task_option = {
            "text": sub_task.name,
            "value": sub_task.name,
        }
        if len(sub_task.get_memo()) > 0:
            description = "\n".join(sub_task.get_memo())
            sub_task_option["description"] = description
        sub_task_options.append(sub_task_option)

    if len(sub_task_options) > 0:
        block_builder = block_builder.add_checkboxes_action(action_id="sub-task-checked",
                                                            options=sub_task_options)
    block_builder = block_builder.add_button_action(action_id="schedule-button",
                                                    text="完了",
                                                    value="complete-task",
                                                    style="primary")
    block_builder = block_builder.add_button_action(action_id="change",
                                                    text="変更",
                                                    value="change-schedule",
                                                    style="danger")

    context = {
        "category": schedule.category,
        "task_name": schedule.title,
        "date": schedule.start.date().isoformat(),
    }
    block_builder = block_builder.add_context(text=json.dumps(context))

    blocks = block_builder.build()
    logger.info(blocks)

    channel = ChannelType.SCHEDULE if not IS_TEST else ChannelType.TEST
    if not is_debug:
        SLACK_BOT.chat_postMessage(channel=channel.value,
                                text=schedule.title,
                                blocks=blocks)
    else:
        logger.info(channel.value)
        logger.info(schedule.title)
        logger.info(blocks)

if __name__ == "__main__":
    logger.debug("debug mode")
    print(handler({}, {}))
