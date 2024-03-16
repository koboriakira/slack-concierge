from dataclasses import dataclass

from domain.channel.channel_type import ChannelType


@dataclass(frozen = True)
class Thread:
    channel_id: str | None
    event_ts: str | None
    thread_ts: str | None

    @staticmethod
    def create(channel_id: str|None = None, event_ts: str|None = None, thread_ts:str|None = None) -> "Thread":
        return Thread(
          channel_id = channel_id or ChannelType.BOT_DM.value,
          event_ts = event_ts or thread_ts,
          thread_ts = thread_ts or event_ts,
        )
