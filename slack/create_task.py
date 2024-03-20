import logging
import os

from infrastructure.api.lambda_notion_api import LambdaNotionApi
from usecase.service.task_generator import TaskGenerator
from util.datetime import convert_to_datetime_or_date
from util.error_reporter import ErrorReporter

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if os.environ.get("ENVIRONMENT") == "dev":
    logger.setLevel(logging.DEBUG)

def handler(event: dict, context: dict) -> None:  # noqa: ARG001
    try:
        task_generator = TaskGenerator(notion_api=LambdaNotionApi())
        task_generator.add_scheduled_task(
            title=event["title"],
            start_datetime=convert_to_datetime_or_date(event["datetime"]))
    except:  # noqa: E722
        ErrorReporter.execute()
        return {"status": "error"}

if __name__ == "__main__":
    # python -m create_task
    logger.debug("debug mode")
    event = {"title": "\u98a8\u5442\u6383\u9664\u3010\u30eb\u30fc\u30c6\u30a3\u30f3\u3011", "datetime": "2024-02-11"}
    context = {}
    print(handler(event, context))
