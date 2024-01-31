import os
import json
import logging
from slack_sdk.web import WebClient
from usecase.love_spotify_track import LoveSpotifyTrack
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from infrastructure.api.lambda_spotify_api import LambdaSpotifyApi

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_BOT = WebClient(token=SLACK_BOT_TOKEN)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if os.environ.get("ENVIRONMENT") == "dev":
    logger.setLevel(logging.DEBUG)

love_spotify_track = LoveSpotifyTrack(
    client=SLACK_BOT,
    notion_api=LambdaNotionApi(),
    spotify_api=LambdaSpotifyApi(),
)

def handler(event, context):
    print("event", event)
    track_id = event["track_id"]
    channel_id = event["channel_id"]
    thread_ts = event["thread_ts"]
    love_spotify_track.handle(track_id=track_id, channel_id=channel_id, thread_ts=thread_ts)

if __name__ == "__main__":
    # python -m love_spotify_track
    logger.debug("debug mode")
    event = {}
    context = {}
    print(handler(event, context))
