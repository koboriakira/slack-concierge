from slack_sdk.web import WebClient
from typing import Optional
import logging

class SlackClientWrapper:
    def __init__(self, client: WebClient, logger: Optional[logging.Logger] = None):
        self.client = client
        self.logger = logger or logging.getLogger(__name__)

    def reactions_add(self, channel: str, name: str, timestamp: str) -> None:
        try:
            self.client.reactions_add(
                channel=channel,
                name=name,
                timestamp=timestamp
            )
        except Exception as e:
            self.logger.warning("リアクションをつけられませんでした。")


    def is_reacted(self, name: str, channel: str, timestamp: str) -> None:
        try:
            response = self.client.reactions_get(
                channel=channel,
                timestamp=timestamp
            )
            message = response["message"]
            if "reactions" not in message:
                return True
            reactions = message["reactions"]
            for reaction in reactions:
                if reaction["name"] == name:
                    return False
            return True
        except Exception as e:
            self.logger.debug(e)
            self.logger.warning("リアクションをつけられませんでした。")

if __name__ == "__main__":
    # python -m infrastructure.slack.slack_client_wrapper
    import os
    logging.basicConfig(level=logging.DEBUG)
    suite = SlackClientWrapper(
        client=WebClient(token=os.environ["SLACK_BOT_TOKEN"]),
        logger=logging.getLogger(__name__)
    )
    print(suite.valid_not_reacted(name="white_check_mark", channel="C05GUTE35RU", timestamp="1706268941.142659"))
