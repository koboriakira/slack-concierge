
import os
from datetime import datetime, timedelta

from slack_sdk.web import WebClient

from domain.channel.channel_type import ChannelType
from domain.schedule.achivement_repository import AchievementRepository
from domain.user.user_kind import UserKind
from util.datetime import jst_now


class RemindToRecordAchievementUseCase:
    SLACK_CHANNEL = ChannelType.NOTIFICATION.value

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
            slack_channel: str|None = None,
            ) -> None:
        # 初期値の整理
        start = start or jst_now() - timedelta(hours=2)
        end = end or jst_now()
        slack_channel = slack_channel or self.SLACK_CHANNEL

        # 実績の取得
        achievements = self.achievement_repository.search(
            start=start,
            end=end,
        )

        # 実績がある場合は通知しない
        if len(achievements) > 0:
            return

        # 実績が見つからない場合は通知する
        user_mention = UserKind.KOBORI_AKIRA.mention()
        self.slack_client.chat_postMessage(
            channel=slack_channel,
            text=f"{user_mention}\n実績を記録しましょう！",
        )
