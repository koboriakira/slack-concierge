import contextlib
import logging
from abc import ABCMeta, abstractmethod

from slack_sdk.web import WebClient

ERROR_TEXT_AND_BLOCK_IS_NONE = "text と blocks のどちらかは必ず指定してください。"
ERROR_TEXT_CLIENT_NOT_SPECIFIED = "client は必ず指定してください。"


class SlackClientWrapper(metaclass=ABCMeta):
    @abstractmethod
    def reactions_add(self, name: str, channel: str, timestamp: str, exception_enabled: bool = False) -> None:
        pass

    @abstractmethod
    def is_reacted(self, name: str, channel: str, timestamp: str) -> bool:
        pass

class SlackClientWrapperImpl(SlackClientWrapper):
    def __init__(self, client: WebClient, logger: logging.Logger | None = None) -> None:
        self.client = client
        self.logger = logger or logging.getLogger(__name__)

    def reactions_add(self, name: str, channel: str, timestamp: str, exception_enabled: bool = False) -> None:
        if not exception_enabled:
            with contextlib.suppress(Exception):
                self.client.reactions_add(
                    channel=channel,
                    name=name,
                    timestamp=timestamp,
                )
                return
        self.client.reactions_add(
                    channel=channel,
                    name=name,
                    timestamp=timestamp,
                )


    def is_reacted(self, name: str, channel: str, timestamp: str) -> bool:
        response = self.client.reactions_get(
            channel=channel,
            timestamp=timestamp,
        )
        message = response["message"]
        if "reactions" not in message:
            return False
        reactions = message["reactions"]
        return any(reaction["name"] == name for reaction in reactions)

class SlackClientWrapperMock(SlackClientWrapper):
    def reactions_add(self, name: str, channel: str, timestamp: str, exception_enabled: bool = False) -> None:
        pass

    def is_reacted(self, name: str, channel: str, timestamp: str) -> bool:
        return True

if __name__ == "__main__":
    # python -m infrastructure.slack.slack_client_wrapper
    import os
    logging.basicConfig(level=logging.DEBUG)
    suite = SlackClientWrapper(
        client=WebClient(token=os.environ["SLACK_BOT_TOKEN"]),
        logger=logging.getLogger(__name__),
    )
    print(suite.valid_not_reacted(name="white_check_mark", channel="C05GUTE35RU", timestamp="1706268941.142659"))
