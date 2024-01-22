from typing import Optional, Any
from util.custom_logging import get_logger
import json

logger = get_logger(__name__)

class BaseMessage:
    client_msg_id: str
    type: str
    text: str
    user: str
    ts: str
    blocks: list
    team: str
    attachments: list[dict[str, Any]]

    def __init__(self, client_msg_id: str, type: str, text: str, user: str, ts: str, blocks: list, team: str, attachments: list[dict[str, Any]]) -> None:
        self.client_msg_id = client_msg_id
        self.type = type
        self.text = text
        self.user = user
        self.ts = ts
        self.blocks = blocks
        self.team = team
        self.attachments = attachments

    @classmethod
    def from_dict(cls, params: dict) -> "BaseMessage":
        return BaseMessage(
            client_msg_id=params["client_msg_id"],
            type=params["type"],
            text=params["text"],
            user=params["user"],
            ts=params["ts"],
            blocks=params["blocks"],
            team=params["team"],
            attachments=params["attachments"] if "attachments" in params else [],
        )

    def from_kobori(self) -> bool:
        return self.user == "U04PQMBCFNE"


# TODO: どういうメッセージがあるか調べて、ちゃんとネーミングする
class ExtendedMessage(BaseMessage):
    channel_type: Optional[str] = None
    event_ts: Optional[str] = None
    channel: Optional[str] = None

    def __init__(self,
                 client_msg_id: str,
                 type: str,
                 text: str,
                 user: str,
                 ts: str,
                 blocks: list,
                 team: str,
                 attachments: list[dict[str, Any]],
                 channel: Optional[str],
                 event_ts: Optional[str],
                 channel_type: Optional[str],
                 ) -> None:
        super().__init__(client_msg_id, type, text, user, ts, blocks, team, attachments)
        self.channel = channel
        self.event_ts = event_ts
        self.channel_type = channel_type

    @staticmethod
    def from_dict(params: dict) -> "ExtendedMessage":
        logger.debug(json.dumps(params))

        return ExtendedMessage(
            client_msg_id=params["client_msg_id"],
            type=params["type"],
            text=params["text"],
            user=params["user"],
            ts=params["ts"],
            blocks=params["blocks"],
            team=params["team"],
            attachments=params["attachments"] if "attachments" in params else [],
            channel=params["channel"] if "channel" in params else None,
            event_ts=params["event_ts"] if "event_ts" in params else None,
            channel_type=params["channel_type"] if "channel_type" in params else None,
        )
