import json

from infrastructure.task.notion_task_repository import NotionTaskRepository
from usecase.complete_task import CompleteTask
from util.error_reporter import ErrorReporter

task_repository = NotionTaskRepository()
usecase = CompleteTask(task_repository=task_repository)

def handler(event:dict, context:dict) -> dict:  # noqa: ARG001
    try:
        request = json.loads(event["Records"][0]["body"])
        page_id = request["page_id"]
        usecase.handle(task_page_id=page_id)
        return {"statusCode": 200}
    except:
        message = f"complete task error. event: {event}"
        ErrorReporter().execute(message=message)
        raise
