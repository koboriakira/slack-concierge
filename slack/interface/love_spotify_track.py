import json

from slack_bolt import Ack, App
from slack_sdk.web import WebClient

from usecase.service.sqs_service import SqsService
from util.custom_logging import get_logger
from util.error_reporter import ErrorReporter
from util.slack_client_wrapper import SlackClientWrapperImpl

ACTION_ID = "LOVE_SPOTIFY_TRACK"

logger = get_logger(__name__)

def just_ack(ack: Ack) -> None:
    ack()

def love_spotify_track(body: dict, client: WebClient) -> None:
    logger.info("love_spotify_track")
    try:
        # ボタンに埋め込まれたvalueを取得。これがtrack_idになる
        action = body["actions"][0]
        track_id = action["value"]

        # 返信用にchannel_id、thread_tsを取得
        channel_id = body["channel"]["id"]
        thread_ts = body["message"]["ts"]

        # Reactionのスタンプをつける
        slack_client_wrapper = SlackClientWrapperImpl(client=client)
        slack_client_wrapper.reactions_add(name="heart", channel=channel_id, timestamp=thread_ts)

        logger.debug(json.dumps(body))
        service = SqsService()
        service.send(
            queue_url="https://sqs.ap-northeast-1.amazonaws.com/743218050155/SlackConcierge-LoveSpotifyTrackQueue80A7F4D3-W3eMtBDoeTka",
            message={
                "track_id": track_id,
                "channel_id": channel_id,
                "thread_ts": thread_ts,
            })
    except:  # noqa: E722
        ErrorReporter().execute()

def shortcut_love_spotify_track(app: App) -> App:
    app.action(ACTION_ID)(
        ack=just_ack,
        lazy=[love_spotify_track],
    )
    return app
