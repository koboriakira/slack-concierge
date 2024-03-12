import os

from slack_sdk import WebClient

from domain.channel.thread import Thread
from domain.music.music_repository import MusicRepository, NotionMusicRepository
from domain.music.spotify_api import SpotifyApi
from infrastructure.music.lambda_spotify_api import LambdaSpotifyApi


class LoveSpotifyTrack:
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
         track = self.spotify_api.find_track(track_id=track_id)
         self.spotify_api.love_track(track_id=track_id)
         self.music_repository.save(
             track=track,
             slack_thread=Thread(channel_id=channel_id, thread_ts=thread_ts),
          )
