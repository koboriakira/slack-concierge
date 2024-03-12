import os

from slack_sdk import WebClient

from domain.channel.thread import Thread
from domain.music.music_repository import MusicRepository, NotionMusicRepository
from domain.music.spotify_api import SpotifyApi
from infrastructure.music.lambda_spotify_api import LambdaSpotifyApi


class ErrorReporter:
    def __init__(self, client: WebClient|None=None) -> None:
        self.client = client or WebClient(token=os.environ["SLACK_BOT_TOKEN"])

    def execute(self, slack_channel: str|None, slack_thread_ts: str|None) -> None:
        import sys
        import traceback
        exc_info = sys.exc_info()
        t, v, tb = exc_info
        formatted_exception = "\n".join(
            traceback.format_exception(t, v, tb))
        text=f"analyze_inbox: error ```{formatted_exception}```"
        self.client.chat_postMessage(
            text=text,
            channel=slack_channel or "C04Q3AV4TA5",
            thread_ts=slack_thread_ts)

class LoveSpotifyUseCase:
    def __init__(
            self,
            slack_bot_client: WebClient|None = None,
            slack_user_client: WebClient|None = None,
            music_repository: MusicRepository|None = None,
            spotify_api: SpotifyApi|None = None,
            ) -> None:
        self.slack_bot_client = slack_bot_client or WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        self.slack_user_client = slack_user_client or WebClient(token=os.environ["SLACK_USER_TOKEN"])
        self.music_repository = music_repository or NotionMusicRepository()
        self.spotify_api = spotify_api or LambdaSpotifyApi()

    def execute(self, track_id: str, channel_id: str, thread_ts: str) -> None:
        try:
            track = self.spotify_api.find_track(track_id=track_id)
            self.spotify_api.love_track(track_id=track_id)
            self.music_repository.save(
                track=track,
                slack_thread=Thread(channel_id=channel_id, thread_ts=thread_ts),
            )
        except:
            ErrorReporter().execute(slack_channel=channel_id, slack_thread_ts=thread_ts)
