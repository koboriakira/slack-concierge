
import os
from datetime import datetime, timedelta

from slack_sdk.web import WebClient

from domain.channel.thread import Thread
from domain.schedule.achievement_repository import AchievementRepository
from util.datetime import jst_now


class RemindToRecordAchievementUseCase:

    def __init__(
            self,
            achievement_repository: AchievementRepository|None = None,
            slack_client: WebClient|None = None) -> None:
        self.achievement_repository = achievement_repository
        self.slack_client = slack_client or WebClient(token=os.environ["SLACK_BOT_TOKEN"])

    def execute(
            self,
            start: datetime|None = None,
            end: datetime|None = None,
            slack_thread: Thread|None = None,
            ) -> None:
        # 初期値の整理
        start = start or jst_now() - timedelta(hours=2)
        end = end or jst_now()
        slack_thread = slack_thread or Thread.empty()

        # 実績の取得
        achievements = self.achievement_repository.search(
            start=start,
            end=end,
        )

        # 実績がある場合は通知しない
        if len(achievements) > 0:
            return

        # 実績が見つからない場合は通知する
        self.slack_client.chat_postMessage(
            channel=slack_thread.channel_id,
            text="実績を記録しましょう！",
        )
