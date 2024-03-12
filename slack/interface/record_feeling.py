import json
import logging
from slack_sdk.web import WebClient
from slack_bolt import App, Ack
from util.logging_traceback import logging_traceback
from util.custom_logging import get_logger
from domain.message import BaseMessage
from domain.channel import Channel
from usecase.love_spotify_track import LoveSpotifyTrack
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from slack.infrastructure.music.lambda_spotify_api import LambdaSpotifyApi
from usecase.record_feeling import RecordFeeling as RecordFeelingUsecase
from domain.view.view import View


ACTION_ID = "record-feeling"
VIEW_CALLBACK_ID = "record-feeling-modal"

logger = get_logger(__name__)

def just_ack(ack: Ack):
    ack()

def record_feeling_modal(body: dict, client: WebClient):
    logger.info("record_feeling")
    try:
        # usecase = LoveSpotifyTrack(
        #     client=client,
        #     notion_api=LambdaNotionApi(),
        #     spotify_api=LambdaSpotifyApi(),
        # )
        trigger_id = body["trigger_id"]

        action = body["actions"][0]
        notion_page_block_id = action["value"]

        # # 返信用にchannel_id、thread_tsを取得
        channel_id = body["channel"]["id"]
        thread_ts = body["message"]["ts"]

        logger.debug(json.dumps(body))
        usecase = RecordFeelingUsecase(notion_api=LambdaNotionApi(), client=client)
        usecase.handle_modal(notion_page_block_id=notion_page_block_id,
                             channel=channel_id,
                             thread_ts=thread_ts,
                             trigger_id=trigger_id,
                             callback_id=VIEW_CALLBACK_ID)
    except Exception as err:
        import sys
        logging_traceback(err, sys.exc_info())

def record_feeling(logger: logging.Logger, view: dict, client: WebClient):
    try:
        view_model = View(view)
        state = view_model.get_state()
        context = view_model.get_context()
        channel = context.channel_id
        thread_ts = context.thread_ts
        block_id = context.get_string("block_id")
        feeling_value = state.get_text_input_value(action_id="feeling")
        logger.debug(feeling_value)
        logger.debug(block_id)
        logger.debug(channel)
        logger.debug(thread_ts)
        usecase = RecordFeelingUsecase(notion_api=LambdaNotionApi(), client=client)
        usecase.handle(block_id=block_id, feeling=feeling_value, channel=channel, thread_ts=thread_ts)
    except Exception as err:
        import sys
        logging_traceback(err, sys.exc_info())

def action_record_feeling(app: App):
    app.action(ACTION_ID)(
        ack=just_ack,
        lazy=[record_feeling_modal],
    )
    app.view(VIEW_CALLBACK_ID)(
        ack=just_ack,
        lazy=[record_feeling],
    )

    return app
