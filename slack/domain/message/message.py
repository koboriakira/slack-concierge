from dataclasses import dataclass


@dataclass(frozen=True)
class Message:
    client_msg_id: str
    type: str
    text: str
    user: str
    ts: str
    blocks: list
    team: str
    channel: str
    event_ts: str
    channel_type: str

    def from_kobori(self) -> bool:
        return self.user == "U04PQMBCFNE"
