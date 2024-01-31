import json
from slack_sdk.web import WebClient
from slack_bolt import App, Ack
from util.logging_traceback import logging_traceback
from util.custom_logging import get_logger
from usecase.love_spotify_track import LoveSpotifyTrack
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from infrastructure.api.lambda_spotify_api import LambdaSpotifyApi
from usecase.service.sqs_service import SqsService

ACTION_ID = "LOVE_SPOTIFY_TRACK"

logger = get_logger(__name__)

def just_ack(ack: Ack):
    ack()

def love_spotify_track(body: dict, client: WebClient):
    logger.info("love_spotify_track")
    try:
        usecase = LoveSpotifyTrack(
            client=client,
            notion_api=LambdaNotionApi(),
            spotify_api=LambdaSpotifyApi(),
        )

        # ボタンに埋め込まれたvalueを取得。これがtrack_idになる
        action = body["actions"][0]
        track_id = action["value"]

        # 返信用にchannel_id、thread_tsを取得
        channel_id = body["channel"]["id"]
        thread_ts = body["message"]["ts"]

        logger.debug(json.dumps(body))
        service = SqsService()
        service.send(
            queue_url="https://sqs.ap-northeast-1.amazonaws.com/743218050155/SlackConcierge-LoveSpotifyTrackQueue80A7F4D3-W3eMtBDoeTka",
            message={
                "track_id": track_id,
                "channel_id": channel_id,
                "thread_ts": thread_ts
            })
    except Exception as err:
        import sys
        logging_traceback(err, sys.exc_info())

def shortcut_love_spotify_track(app: App):
    app.action(ACTION_ID)(
        ack=just_ack,
        lazy=[love_spotify_track],
    )
    return app
