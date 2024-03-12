import json
import logging
import os

from slack_sdk.web import WebClient

from domain.music.music_repository import NotionMusicRepository
from infrastructure.music.lambda_spotify_api import LambdaSpotifyApi
from usecase.love_spotify_use_case import LoveSpotifyUseCase

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if os.environ.get("ENVIRONMENT") == "dev":
    logger.setLevel(logging.DEBUG)


usecase = LoveSpotifyUseCase(
    slack_bot_client=WebClient(token=os.environ["SLACK_BOT_TOKEN"]),
    slack_user_client=WebClient(token=os.environ["SLACK_USER_TOKEN"]),
    spotify_api=LambdaSpotifyApi(),
    music_repository=NotionMusicRepository(),
)

def handler(event: dict, context:dict) -> None:
    request = json.loads(event["Records"][0]["body"])
    print("request", request)
    track_id = request["track_id"]
    channel_id = request["channel_id"]
    thread_ts = request["thread_ts"]
    usecase.execute(track_id=track_id, channel_id=channel_id, thread_ts=thread_ts)
