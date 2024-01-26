import logging
import re
import json
from slack_sdk.web import WebClient
from slack_bolt import App, Ack, Say
from slack_bolt.context.context import BoltContext
from util.logging_traceback import logging_traceback
from domain.message import ExtendedMessage
from domain.channel import ChannelType
from util.environment import Environment

def just_ack(ack: Ack):
    ack()

def react(message:dict, say: Say, context: BoltContext, logger: logging.Logger):
    if Environment.is_dev():
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.DEBUG)
    logger.info("react")

    try:
        logger.debug(json.dumps(message, ensure_ascii=False))
        message_model = ExtendedMessage(**message)
        if not message_model.from_kobori():
            return
        logging.debug("context: " + str(context))
    except Exception as e:
        import sys
        exc_info = sys.exc_info()
        logging_traceback(e, exc_info)


def message_react_user_post(app: App):
    app.message(re.compile(".*"))(
        ack=just_ack,
        lazy=[react],
    )

    return app
