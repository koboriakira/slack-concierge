from abc import ABCMeta, abstractmethod

from domain.channel.thread import Thread
from domain.infrastructure.api.notion_api import NotionApi
from domain.music.track import Track


class MusicRepository(metaclass=ABCMeta):
    @abstractmethod
    def save(self, track: Track) -> bool:
        pass

class NotionMusicRepository(MusicRepository):
    def __init__(self, notion_api: NotionApi|None = None) -> None:
        from infrastructure.api.lambda_notion_api import LambdaNotionApi
        self.notion_api = notion_api or LambdaNotionApi()

    def save(self, track: Track, slack_thread: Thread|None) -> bool:
        data = track.to_dict()
        if slack_thread:
            data["slack_channel"] = slack_thread.channel_id
            data["slack_thread_ts"] = slack_thread.thread_ts
        self.notion_api.post(path="music", data=data)
        return True
