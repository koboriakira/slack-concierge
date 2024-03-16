import os

from slack_sdk.web import WebClient

from infrastructure.schedule.achievement_repository_impl import AchivementRepositoryImpl
from usecase.remind_to_record_achivement_use_case import RemindToRecordAchievementUseCase
from util.error_reporter import ErrorReporter

usecase = RemindToRecordAchievementUseCase(
    achievement_repository=AchivementRepositoryImpl(),
    slack_client=WebClient(token=os.environ["SLACK_BOT_TOKEN"]),
)

def handler(event: dict, context:dict) -> None:  # noqa: ARG001
    try:
        usecase.execute()
    except:
        ErrorReporter().execute()
        raise

if __name__ == "__main__":
    # python -m slack.remind_to_record_achivement
    handler({}, {})
